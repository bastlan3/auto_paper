const { exec } = require('child_process');
const path = require('path');

const pyInstallerCommand = `pyinstaller --name server --onefile --distpath ${path.join(
  __dirname,
  'dist'
)} ${path.join(__dirname, '..', 'server.py')}`;

exec(pyInstallerCommand, (err, stdout, stderr) => {
  if (err) {
    console.error(err);
    return;
  }
  console.log(stdout);
  console.error(stderr);
});
