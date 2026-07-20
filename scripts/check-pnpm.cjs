const fs = require('fs');
const path = require('path');

for (const fileName of ['package-lock.json', 'yarn.lock']) {
  try {
    fs.rmSync(path.join(process.cwd(), fileName), { force: true });
  } catch {
    // Ignore cleanup failures; the install should continue.
  }
}

const userAgent = process.env.npm_config_user_agent || '';
if (!userAgent.startsWith('pnpm/')) {
  console.error('Use pnpm instead');
  process.exit(1);
}
