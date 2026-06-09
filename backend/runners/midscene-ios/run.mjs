import path from 'node:path';
import { createRequire } from 'node:module';

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = '';
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => {
      data += chunk;
    });
    process.stdin.on('end', () => resolve(data));
    process.stdin.on('error', reject);
  });
}

function asArray(value) {
  if (!value) {
    return [];
  }
  return Array.isArray(value) ? value.filter(Boolean) : [String(value)];
}

function serializeError(error) {
  return {
    name: error?.name || 'Error',
    message: error?.message || String(error),
    stack: error?.stack,
  };
}

const capturedLogs = [];
const originalConsole = {
  log: console.log,
  warn: console.warn,
  error: console.error,
};

console.log = (...args) => {
  capturedLogs.push({ level: 'info', message: args.map(String).join(' ') });
};
console.warn = (...args) => {
  capturedLogs.push({ level: 'warning', message: args.map(String).join(' ') });
};
console.error = (...args) => {
  capturedLogs.push({ level: 'error', message: args.map(String).join(' ') });
};

async function main() {
  const startedAt = Date.now();
  const input = await readStdin();
  const payload = input ? JSON.parse(input) : {};
  const midsceneRepoDir = payload.midsceneRepoDir;

  if (!midsceneRepoDir) {
    throw new Error('midsceneRepoDir is required');
  }

  const requireFromIos = createRequire(
    path.join(midsceneRepoDir, 'packages', 'ios', 'package.json'),
  );
  const { agentFromWebDriverAgent } = requireFromIos(
    path.join(midsceneRepoDir, 'packages', 'ios', 'dist', 'lib', 'index.js'),
  );

  const steps = asArray(payload.steps);
  const assertions = asArray(payload.assertions);
  const stepResults = [];
  const assertionResults = [];
  let agent;

  try {
    agent = await agentFromWebDriverAgent({
      wdaHost: payload.wda_host || payload.wdaHost || '127.0.0.1',
      wdaPort: payload.wda_port || payload.wdaPort || 8100,
      wdaMjpegPort: payload.wda_mjpeg_port || payload.wdaMjpegPort,
      deviceId: payload.device_id || payload.deviceId,
    });

    if (payload.app) {
      const launchStartedAt = Date.now();
      try {
        await agent.launch(payload.app);
        stepResults.push({
          index: 0,
          instruction: `启动 ${payload.app}`,
          success: true,
          duration: (Date.now() - launchStartedAt) / 1000,
        });
      } catch (error) {
        stepResults.push({
          index: 0,
          instruction: `启动 ${payload.app}`,
          success: false,
          duration: (Date.now() - launchStartedAt) / 1000,
          error: serializeError(error),
        });
        throw error;
      }
    }

    for (const [index, instruction] of steps.entries()) {
      const stepStartedAt = Date.now();
      try {
        const output = await agent.aiAction(instruction);
        stepResults.push({
          index: index + 1,
          instruction,
          success: true,
          duration: (Date.now() - stepStartedAt) / 1000,
          output,
        });
      } catch (error) {
        stepResults.push({
          index: index + 1,
          instruction,
          success: false,
          duration: (Date.now() - stepStartedAt) / 1000,
          error: serializeError(error),
        });
        throw error;
      }
    }

    for (const [index, assertion] of assertions.entries()) {
      const assertionStartedAt = Date.now();
      const result = await agent.aiAssert(assertion, undefined, {
        keepRawResponse: true,
      });
      assertionResults.push({
        index: index + 1,
        assertion,
        success: Boolean(result?.pass),
        duration: (Date.now() - assertionStartedAt) / 1000,
        thought: result?.thought,
        message: result?.message,
      });
    }

    const success =
      stepResults.every((item) => item.success) &&
      assertionResults.every((item) => item.success);

    return {
      success,
      task_name: payload.task_name || payload.taskName || 'Midscene iOS run',
      steps: stepResults,
      assertions: assertionResults,
      duration: (Date.now() - startedAt) / 1000,
      rawLogs: capturedLogs,
      reportFile: agent.reportFile,
    };
  } finally {
    if (agent?.destroy) {
      await agent.destroy();
    }
  }
}

main()
  .then((result) => {
    process.stdout.write(JSON.stringify(result));
  })
  .catch((error) => {
    const result = {
      success: false,
      error: serializeError(error),
      steps: [],
      assertions: [],
      rawLogs: capturedLogs,
    };
    process.stdout.write(JSON.stringify(result));
    originalConsole.error(error);
    process.exitCode = 1;
  });
