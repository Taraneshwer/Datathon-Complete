const userAgent = process.env.npm_config_user_agent || '';
if (!userAgent.startsWith('npm/')) {
  console.error('This workspace is configured for npm. Please run the install commands with npm.');
  process.exit(1);
}
