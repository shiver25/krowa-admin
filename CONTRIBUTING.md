# Contributing to Krowa Admin

Contributions should keep checks optional, configurable, and safe to run in an
interactive login shell.

## Adding a Check

When adding a new check, complete every step in this list:

1. Add the check function to the appropriate module in `checks/`.
2. Import the function in `service-status.py`.
3. Read its settings from the `checks` section of the configuration.
4. Call it conditionally from `generate_status_report()`.
5. Document the available settings in `config.example.yaml`.
6. Enable the check in `/etc/krowa-admin/config.yaml` on the test host.
7. Test both `enabled: true` and `enabled: false`.

`config.example.yaml` is only a versioned template. The program reads the
host-specific configuration from `/etc/krowa-admin/config.yaml`. Adding an
option to the template does not enable it on an existing installation.

## Check Design

- Return report text from check functions; do not print from inside a check.
- Add the returned text to the main report in `generate_status_report()`.
- Use argument lists with `subprocess` instead of `shell=True`.
- Add a timeout to commands that can block.
- Catch expected command, timeout, and missing-file errors.
- Never include secrets such as K3s token contents in report output.
- Keep specialized checks independent from the general systemd services list.

## Local Validation

Compile all Python modules:

```bash
python3 -m compileall -q service-status.py formatting.py checks
```

Run the source version. It still reads `/etc/krowa-admin/config.yaml`:

```bash
python3 service-status.py
```

Check the diff for whitespace errors:

```bash
git diff --check
```

## Package Validation

Build both package formats:

```bash
VERSION=0.2.0 ./build_and_test/build_in_docker.sh
```

Test installation and execution in clean containers:

```bash
./build_and_test/deb_test_in_docker.sh
./build_and_test/rpm_test_in_docker.sh
```

Generated files in `dist/` are release artifacts and should not be committed.
