# Keystone Python Client

The official Python client for the Keystone API.

A quickstart guide for project developers is provided below.
For the full Keystone project documentation, see [keystone.bhpc.dev](https://keystone.bhpc.dev).

## Developer Setup

This project uses the [Poetry](https://python-poetry.org/) package manager.
To initialize a new environment, start by defining your desired Python interpreter:

```bash
poetry env use python3
```

Next, install the project and its dependencies.
The `dev` dependency group is optional, but includes useful utilities for running application tests:

```bash
poetry install --with dev
```

## Common Tasks

### Running Tests

Application tests are organized by testing strategy.
Unit tests are used to verify components in isolation and require no external services.
Function tests validate package integration against a live API server and require a running Keystone API instance.

#### Unit Tests

Unit tests are executed using the standard `unittest` library:

```bash
python -m unittest discover -s ./tests/unit_tests
```

Alternatively, the `coverage` utility can also be used to execute tests and report the resulting coverage:

```bash
coverage run -m unittest discover -s ./tests/unit_tests
coverage report
```

#### Function Tests

Function tests are used to validate the client against a running API server.
The following environmental variables are used to configure connection settings against the upstream API:

| Variable            | Description                                       | Default                 |
|---------------------|---------------------------------------------------|-------------------------|
| `TEST_API_HOST`     | URL of the Keystone API instance to test against. | `http://localhost:8000` |
| `TEST_API_USER`     | Username used to authenticate with the API.       | `admin`                 |
| `TEST_API_PASSWORD` | Password used to authenticate with the API.       | `quickstart`            |

Once the target API instance is configured and running, function tests are executed using the standard library `unittest` framework:

```bash
python -m unittest discover -s ./tests/function_tests
```
