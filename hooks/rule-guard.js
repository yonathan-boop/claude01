'use strict';

/**
 * SISTEM PAGAR FISIK KERNEL (RULE ENFORCEMENT ENGINE 01)
 *
 * Alur Sistem dalam Bahasa Manusia:
 * 1. Setiap kali Claude Code ingin menjalankan tool (Write, Edit, PowerShell, Bash),
 *    perintah dicegat di sini SEBELUM menyentuh sistem operasi Windows.
 * 2. Data input dibaca dari stdin dalam format JSON.
 * 3. File aturan permanen ('permanent-rules.json') dibaca untuk mencocokkan target/pola terlarang.
 * 4. Jika ada pelanggaran, sistem memutus eksekusi seketika (Exit code 2) dan mengirim pesan blokir.
 * 5. Jika aman, sistem mengizinkan eksekusi tanpa hambatan (Exit code 0).
 */

const fs = require('fs');
const path = require('path');

const userHome = process.env.USERPROFILE || process.env.HOME || 'C:\\Users\\yonat';
const rulesFile = path.join(userHome, '.claude', 'rules', 'permanent-rules.json');

/**
 * Fungsi: Menyamakan format path Windows agar kebal terhadap variasi garis miring dan huruf besar/kecil.
 * Alur: Mengubah path relatif jadi absolut, huruf kecil semua, dan ganti semua slash ganda menjadi backslash tunggal.
 * Tujuan: Mencegah AI mengelabui pagar dengan trik ../, huruf besar, atau forward slash.
 */
function normalizePath(rawPath, baseDirectory) {
  if (!rawPath) return '';
  const resolvedPath = path.isAbsolute(rawPath) ? path.resolve(rawPath) : path.resolve(baseDirectory || process.cwd(), rawPath);
  return resolvedPath.toLowerCase().replace(/[\/\\]+/g, '\\');
}

/**
 * Fungsi: Mode Darurat (Fail-Closed) bila file aturan rusak atau tidak terbaca.
 * Alur: Jika ada file konfigurasi hilang atau JSON korup, tolak semua operasi apapun dan keluar dengan kode error 2.
 * Tujuan: Jangan biarkan operasi berjalan tanpa perlindungan; lebih baik berhenti daripada sistem rentan rusak.
 */
function failClosed(errMessage) {
  const errOutput = {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny'
    },
    systemMessage: `[FAIL-CLOSED: RULE ENFORCEMENT ENGINE 01 ERROR]\n${errMessage}\nOperasi dihentikan demi keamanan sistem.`
  };
  process.stdout.write(JSON.stringify(errOutput));
  process.stderr.write(`[RULE GUARD ERROR] ${errMessage}\n`);
  process.exit(2);
}

/**
 * Fungsi: Menolak eksekusi tool yang melanggar aturan aktif.
 * Alur: Merangkum identitas aturan yang dilanggar, detail pelanggaran, menulis JSON penolakan ke stdout, dan stop proses.
 * Tujuan: Menghentikan aksi AI sebelum file diubah atau perintah terminal dijalankan.
 */
function blockOperation(rule, detail) {
  const blockOutput = {
    hookSpecificOutput: {
      hookEventName: 'PreToolUse',
      permissionDecision: 'deny'
    },
    systemMessage: `[RULE VIOLATION BLOCKED BY RULE ENFORCEMENT ENGINE 01]\n` +
      `Aturan ID: ${rule.id}\n` +
      `Nama: ${rule.name}\n` +
      `Deskripsi: ${rule.description}\n` +
      `Detail Pelanggaran: ${detail}\n` +
      `Status: EKSEKUSI DITOLAK SEBELUM BERJALAN. Tidak ada perubahan yang terjadi.`
  };
  process.stdout.write(JSON.stringify(blockOutput));
  process.stderr.write(`[BLOCKED BY RULE ENGINE 01] Rule ${rule.id}: ${detail}\n`);
  process.exit(2);
}

// Read stdin
let rawInput = '';
process.stdin.setEncoding('utf8');

process.stdin.on('data', chunk => {
  rawInput += chunk;
});

process.stdin.on('end', () => {
  rawInput = rawInput.replace(/^\uFEFF/, '').trim();
  if (!rawInput) {
    // Empty input, allow
    process.exit(0);
  }

  let input;
  try {
    input = JSON.parse(rawInput);
  } catch (err) {
    failClosed(`Gagal parse input JSON: ${err.message}`);
    return;
  }

  const toolName = input.tool_name || input.toolName || '';
  const toolInput = input.tool_input || input.toolInput || {};
  const cwd = input.cwd || process.cwd() || '';

  // Load rules
  if (!fs.existsSync(rulesFile)) {
    failClosed(`File permanent-rules.json tidak ditemukan di: ${rulesFile}`);
    return;
  }

  let config;
  try {
    const raw = fs.readFileSync(rulesFile, 'utf8').replace(/^\uFEFF/, '').trim();
    config = JSON.parse(raw);
  } catch (err) {
    failClosed(`File aturan korup / tidak valid JSON: ${err.message}`);
    return;
  }

  const activeRules = (config.rules || []).filter(r => r.status === 'active');

  // ---------------------------------------------------------------------------
  // FILTER 1: Proteksi Alat Modifikasi Berkas Langsung (Write, Edit, MultiEdit)
  // Alur: Mengambil path berkas target yang ingin diedit, lalu membandingkannya
  // dengan daftar folder/file terlarang yang ada di aturan permanen.
  // Tujuan: Mencegah Claude merusak file kritis atau folder sensitif secara langsung.
  // ---------------------------------------------------------------------------
  if (['Write', 'Edit', 'MultiEdit'].includes(toolName)) {
    const rawFilePath = toolInput.file_path || toolInput.filePath || toolInput.path || '';
    const targetNorm = normalizePath(rawFilePath, cwd);

    for (const rule of activeRules) {
      if (rule.forbidden_tools && rule.forbidden_tools.includes(toolName)) {
        for (const ruleTarget of (rule.targets || [])) {
          const ruleNorm = normalizePath(ruleTarget, cwd);
          // Cek kesamaan path persis atau apakah target berada di dalam subdirektori terproteksi
          if (targetNorm === ruleNorm || targetNorm.startsWith(ruleNorm + '\\')) {
            blockOperation(rule, `Mencoba menjalankan ${toolName} pada target terproteksi: ${rawFilePath}`);
          }
          // Jika target aturan hanya berupa nama file tanpa path, cek kesamaan nama dasar (basename)
          if (!ruleTarget.includes('\\') && !ruleTarget.includes('/') && path.basename(targetNorm) === ruleNorm) {
            blockOperation(rule, `Mencoba menjalankan ${toolName} pada file terproteksi: ${rawFilePath}`);
          }
        }
      }
    }
  }

  // ---------------------------------------------------------------------------
  // FILTER 2: Proteksi Terminal Shell (PowerShell, Bash)
  // Alur: Memeriksa teks perintah baris shell terhadap daftar regex terlarang
  // (misal push ke repo terlarang, mematikan proses Office, atau manipulasi folder lindung).
  // Tujuan: Mencegah bypass lewat eksekusi skrip command line / PowerShell.
  // ---------------------------------------------------------------------------
  if (['PowerShell', 'Bash'].includes(toolName)) {
    const command = toolInput.command || '';
    const cwdNorm = normalizePath(cwd);

    for (const rule of activeRules) {
      // Cek pola teks perintah terlarang langsung via Regular Expression
      if (rule.terminal_write_patterns) {
        for (const pattern of rule.terminal_write_patterns) {
          const regex = new RegExp(pattern, 'i');
          if (regex.test(command)) {
            blockOperation(rule, `Perintah terminal '${command}' cocok dengan pola terlarang: ${pattern}`);
          }
        }
      }

      // Cek apakah terminal sedang aktif di dalam folder yang dilindungi
      if (rule.targets && rule.targets.length > 0) {
        for (const target of rule.targets) {
          const targetNorm = normalizePath(target);
          const isUnderTarget = cwdNorm === targetNorm || cwdNorm.startsWith(targetNorm + '\\');

          if (isUnderTarget) {
            const gitOrWriteRegex = /\b(git\s+(commit|push|add|rm|reset)|New-Item|Set-Content|Add-Content|Remove-Item|del|rm|>|>>)\b/i;
            if (gitOrWriteRegex.test(command)) {
              blockOperation(rule, `Terminal berada di direktori terproteksi '${target}', dilarang menulis/push: ${command}`);
            }
          }

          // Cek pola berbahaya yang menargetkan nama file terproteksi secara eksplisit
          const baseName = path.basename(target).replace('.', '\\.');
          const destructivePatterns = [
            `>\\s*.*${baseName}`,
            `>>\\s*.*${baseName}`,
            `Set-Content.*${baseName}`,
            `Add-Content.*${baseName}`,
            `Out-File.*${baseName}`,
            `Remove-Item.*${baseName}`,
            `\\b(rm|del|erase)\\b.*${baseName}`,
            `git.*${baseName}.*(commit|push|add)`
          ];

          for (const dp of destructivePatterns) {
            const dRegex = new RegExp(dp, 'i');
            if (dRegex.test(command)) {
              blockOperation(rule, `Perintah terminal terdeteksi mencoba mengubah target terproteksi '${target}': ${command}`);
            }
          }
        }
      }
    }
  }

  // Operasi lolos semua sensor pengawas: izinkan eksekusi tanpa halangan
  process.exit(0);
});
