'use strict';

const fs = require('fs');
const path = require('path');

const userHome = process.env.USERPROFILE || process.env.HOME || 'C:\\Users\\yonat';
const rulesFile = path.join(userHome, '.claude', 'rules', 'permanent-rules.json');

function normalizePath(p, baseDir) {
  if (!p) return '';
  const resolved = path.isAbsolute(p) ? path.resolve(p) : path.resolve(baseDir || process.cwd(), p);
  return resolved.toLowerCase().replace(/[\/\\]+/g, '\\');
}

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

  // Check 1: File modification tools (Write, Edit, MultiEdit)
  if (['Write', 'Edit', 'MultiEdit'].includes(toolName)) {
    const rawFilePath = toolInput.file_path || toolInput.filePath || toolInput.path || '';
    const targetNorm = normalizePath(rawFilePath, cwd);

    for (const rule of activeRules) {
      if (rule.forbidden_tools && rule.forbidden_tools.includes(toolName)) {
        for (const ruleTarget of (rule.targets || [])) {
          const ruleNorm = normalizePath(ruleTarget, cwd);
          // Check exact match or subdirectory match
          if (targetNorm === ruleNorm || targetNorm.startsWith(ruleNorm + '\\')) {
            blockOperation(rule, `Mencoba menjalankan ${toolName} pada target terproteksi: ${rawFilePath}`);
          }
          // If rule target is a single file name (no path separator), check basename match
          if (!ruleTarget.includes('\\') && !ruleTarget.includes('/') && path.basename(targetNorm) === ruleNorm) {
            blockOperation(rule, `Mencoba menjalankan ${toolName} pada file terproteksi: ${rawFilePath}`);
          }
        }
      }
    }
  }

  // Check 2: Terminal Execution (PowerShell, Bash)
  if (['PowerShell', 'Bash'].includes(toolName)) {
    const command = toolInput.command || '';
    const cwdNorm = normalizePath(cwd);

    for (const rule of activeRules) {
      // Check terminal patterns
      if (rule.terminal_write_patterns) {
        for (const pattern of rule.terminal_write_patterns) {
          const regex = new RegExp(pattern, 'i');
          if (regex.test(command)) {
            blockOperation(rule, `Perintah terminal '${command}' cocok dengan pola terlarang: ${pattern}`);
          }
        }
      }

      // Check protected targets in directory/file context
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

  // Allowed - clean pass
  process.exit(0);
});
