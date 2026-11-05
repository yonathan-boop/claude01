import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { exec } from "child_process";
import fs from "fs/promises";
import path from "path";
import http from "http";

const server = new McpServer({
  name: "node01-system-tools",
  version: "1.0.0"
});

const GIT_BASH_PATH = "C:\\Users\\yonat\\Tools\\git\\usr\\bin\\bash.exe";
const NINEROUTER_URL = "http://127.0.0.1:20128/v1/chat/completions";
const NINEROUTER_KEY = "sk-550b04f93399b7a7-cdmmjm-b8b1e5c3";

// Tool 1: PowerShell
server.tool(
  "powershell",
  "Execute a PowerShell command on the host Windows machine with full permissions.",
  {
    command: z.string().describe("The PowerShell command string to execute")
  },
  async ({ command }) => {
    return new Promise((resolve) => {
      exec(
        `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ${JSON.stringify(command)}`,
        { maxBuffer: 10 * 1024 * 1024, timeout: 120000, windowsHide: true },
        (error, stdout, stderr) => {
          let output = "";
          if (stdout) output += stdout;
          if (stderr) output += (output ? "\n--- STDERR ---\n" : "") + stderr;
          if (error && !output) output = error.message;
          resolve({
            content: [{ type: "text", text: output.trim() || "(Command completed with no output)" }],
            isError: !!error
          });
        }
      );
    });
  }
);

// Tool 2: Git Bash
server.tool(
  "bash",
  "Execute a Bash command via Git Bash on the host Windows machine.",
  {
    command: z.string().describe("The bash command to execute")
  },
  async ({ command }) => {
    return new Promise((resolve) => {
      exec(
        `"${GIT_BASH_PATH}" -c ${JSON.stringify(command)}`,
        { maxBuffer: 10 * 1024 * 1024, timeout: 120000, windowsHide: true },
        (error, stdout, stderr) => {
          let output = "";
          if (stdout) output += stdout;
          if (stderr) output += (output ? "\n--- STDERR ---\n" : "") + stderr;
          if (error && !output) output = error.message;
          resolve({
            content: [{ type: "text", text: output.trim() || "(Command completed with no output)" }],
            isError: !!error
          });
        }
      );
    });
  }
);

// Tool 3: Query 9router
server.tool(
  "query_9router",
  "Query the local 9router AI engine (port 20128, model campur) for complex reasoning, code generation, or task delegation.",
  {
    prompt: z.string().describe("The prompt to send to 9router"),
    system_prompt: z.string().optional().describe("Optional system prompt")
  },
  async ({ prompt, system_prompt }) => {
    return new Promise((resolve) => {
      const messages = [];
      if (system_prompt) {
        messages.push({ role: "system", content: system_prompt });
      }
      messages.push({ role: "user", content: prompt });

      const payload = JSON.stringify({
        model: "campur",
        messages,
        stream: false
      });

      const req = http.request(
        {
          hostname: "127.0.0.1",
          port: 20128,
          path: "/v1/chat/completions",
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${NINEROUTER_KEY}`,
            "Content-Length": Buffer.byteLength(payload)
          },
          timeout: 120000
        },
        (res) => {
          let data = "";
          res.on("data", (chunk) => (data += chunk));
          res.on("end", () => {
            try {
              const parsed = JSON.parse(data);
              const text = parsed?.choices?.[0]?.message?.content || data;
              resolve({
                content: [{ type: "text", text }],
                isError: false
              });
            } catch (err) {
              resolve({
                content: [{ type: "text", text: data || err.message }],
                isError: true
              });
            }
          });
        }
      );

      req.on("error", (err) => {
        resolve({
          content: [{ type: "text", text: `9router error: ${err.message}` }],
          isError: true
        });
      });

      req.write(payload);
      req.end();
    });
  }
);

// Tool 4: Read File
server.tool(
  "read_file",
  "Read the contents of a file from disk with UTF-8 encoding.",
  {
    file_path: z.string().describe("Absolute file path")
  },
  async ({ file_path }) => {
    try {
      const content = await fs.readFile(file_path, "utf-8");
      return {
        content: [{ type: "text", text: content }],
        isError: false
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error reading file: ${err.message}` }],
        isError: true
      };
    }
  }
);

// Tool 5: Write File
server.tool(
  "write_file",
  "Write or overwrite a file on disk with the provided content.",
  {
    file_path: z.string().describe("Absolute file path"),
    content: z.string().describe("File content to write")
  },
  async ({ file_path, content }) => {
    try {
      await fs.mkdir(path.dirname(file_path), { recursive: true });
      await fs.writeFile(file_path, content, "utf-8");
      return {
        content: [{ type: "text", text: `Successfully wrote ${Buffer.byteLength(content)} bytes to ${file_path}` }],
        isError: false
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error writing file: ${err.message}` }],
        isError: true
      };
    }
  }
);

// Tool 6: Edit File (string replacement)
server.tool(
  "edit_file",
  "Replace an exact string in a file with new string.",
  {
    file_path: z.string().describe("Absolute file path"),
    old_string: z.string().describe("The exact text to replace"),
    new_string: z.string().describe("The new replacement text")
  },
  async ({ file_path, old_string, new_string }) => {
    try {
      const content = await fs.readFile(file_path, "utf-8");
      if (!content.includes(old_string)) {
        return {
          content: [{ type: "text", text: `Error: old_string not found in ${file_path}` }],
          isError: true
        };
      }
      const updated = content.replace(old_string, new_string);
      await fs.writeFile(file_path, updated, "utf-8");
      return {
        content: [{ type: "text", text: `Successfully replaced text in ${file_path}` }],
        isError: false
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error editing file: ${err.message}` }],
        isError: true
      };
    }
  }
);

// Tool 7: Get Memory
const MEMORY_DIR = "C:\\Users\\yonat\\Desktop\\Claude\\memory";
const MAIN_MEMORY_PATH = path.join(MEMORY_DIR, "MEMORY.md");

server.tool(
  "get_memory",
  "Retrieve permanent memory notes, standing rules, and user preferences.",
  {
    topic: z.string().optional().describe("Optional specific topic file in memory folder (e.g. user-preferences.md)")
  },
  async ({ topic }) => {
    try {
      const targetPath = topic ? path.join(MEMORY_DIR, topic) : MAIN_MEMORY_PATH;
      const content = await fs.readFile(targetPath, "utf-8");
      return {
        content: [{ type: "text", text: content }],
        isError: false
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error reading memory: ${err.message}` }],
        isError: true
      };
    }
  }
);

// Tool 8: Save Memory Note
server.tool(
  "save_memory_note",
  "Append a durable note or learned fact to permanent memory.",
  {
    note: z.string().describe("The durable fact or preference note to append"),
    filename: z.string().optional().describe("Optional memory file name, defaults to MEMORY.md")
  },
  async ({ note, filename }) => {
    try {
      const targetFile = filename ? path.join(MEMORY_DIR, filename) : MAIN_MEMORY_PATH;
      await fs.mkdir(MEMORY_DIR, { recursive: true });
      const entry = `\n- ${note.trim()}\n`;
      await fs.appendFile(targetFile, entry, "utf-8");
      return {
        content: [{ type: "text", text: `Successfully appended note to ${targetFile}` }],
        isError: false
      };
    } catch (err) {
      return {
        content: [{ type: "text", text: `Error saving memory: ${err.message}` }],
        isError: true
      };
    }
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
