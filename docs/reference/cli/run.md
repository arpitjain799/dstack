# dstack run

This command runs a workflow defined in the current Git repo. 

The command provisions the required compute resources (in a configured cloud), fetches the same version of code 
(as you have locally), downloads the deps, and runs the workflow, saves artifacts, and tears down compute resources.

[//]: # (!!! info "NOTE:")
[//]: # (    Make sure to use the CLI from within a Git repo directory.)
[//]: # (    When you run a workflow, dstack detects the current branch, commit hash, and local changes.)

## Usage

<div class="termy">

```shell
$ dstack run --help
Usage: dstack run [-h] [--remote] [-t TAG] [-d] [WORKFLOW] [ARGS ...]

Positional Arguments:
  WORKFLOW              A workflow name
  ARGS                  Override provider arguments
  
  
Optional Arguments:
  --remote              Run the workflow remotely
  -t, --tag TAG         A tag name. Warning, if the tag exists, it will be overridden.
  -d, --detach          Do not poll for status update and logs
  -i IDENTITY_FILE      A path to ssh identity file
```

</div>

## Arguments reference

The following arguments are required:

- `WORKFLOW` - (Required) A name of a workflow defined in 
   one of the YAML files in `./dstack/workflows`.

The following arguments are optional:

- `-t TAG`, `--tag TAG` – (Optional) A tag name. Warning, if the tag exists, it will be overridden.
- `-r`, `--remote` – (Optional) Run the workflow in the cloud.
- `-d`, `--detach` – (Optional) Run the workflow in the detached mode. Means, the `run` command doesn't
  poll for logs and workflow status, but exits immediately.
- `-i IDENTITY_FILE` – (Optional) A path to ssh identity file. Used to establish ssh tunnel with a remote
  runner. Default to `~/.ssh/id_rsa`
- `OPTIONS` – (Optional) Use `OPTIONS` to override workflow parameters defined in the workflow YAML file
- `ARGS` – (Optional) Use `ARGS` to [pass arguments](../../usage/args.md) to the workflow
  (can be accessed via `${{ run.args }}` from the workflow YAML file).
-  `-h`, `--help` – (Optional) Shows help for the `dstack run` command. Combine it with the name of the workflow
   to see how to override workflow parameters defined in the workflow YAML file

!!! info "NOTE:"
    By default, it runs it in the attached mode, so you'll see the output in real-time as your 
    workflow is running.