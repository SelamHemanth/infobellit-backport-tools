# Kernel PR Test Tool
---

Small shell-based toolkit to export recent commits from an kernel tree, inject required metadata (Signed-off-by and Bugzilla), apply patches one-by-one, run a kernel build for each patch, and collect per-patch logs for PR validation.


## Distro Support
---

1. OpenAnolis

## usage
---

* Create configuration (interactive):
```sh
./run.sh --config
```
* Run the test:
```sh
./run.sh --build
```
* Restore the repository to the saved HEAD:
```sh
./run.sh --reset
```

* Remove generated artifacts:
```sh
./run.sh --clean
```
* Help:
```sh
./run.sh --help/-h
```

## Author:
---
`Signed-off-by:` Hemanth Selam <Hemanth.Selam@amd.com>
