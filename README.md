# Personal Finance & Analytics

[![MIT License][license-shield]][license-url]
[![Python][python-shield]][python-url]
[![Vue.js][vue-shield]][vue-url]
[![FastAPI][fastapi-shield]][fastapi-url]
[![Postgres][postgres-shield]][postgres-url]
[![Docker][docker-shield]][docker-url]

## Overview

![Lifecycle][lifecycle-shield]

This full-stack engine is being developed as a personal project to replace manual spreadsheet tracking with a robust automated solution. Transitioning from Google Sheets to this custom engine ensures data integrity, allows for complex analyses, and facilitates automated household inventory management.

Feel free to adapt this project to your needs or use it as a starting point for your own project.

<!-- TODO: add example images -->
The current (actively changing) visual or the app:
![Current app visual](/Example.png)

<!-- TODO: showcase current data model -->


## Built With

### Backend & Containerisation

[![Python][python-shield]][python-url]
[![FastAPI][fastapi-shield]][fastapi-url]
[![Postgres][postgres-shield]][postgres-url]
[![Docker][docker-shield]][docker-url]

### Frontend

[![Vue.js][vue-shield]][vue-url]

### Development

[![pre-commit][precommit-shield]][precommit-url]
[![PEP8][pep8-shield]][pep8-url]


## Getting Started

Ensure you have **Docker** and **Docker Compose** installed.

#### 1. Clone the repository

```bash
git clone https://github.com/01011001010/Finance-Manager.git
cd Finance-Manager
```
#### 2. Spin up the environment

```bash
docker compose up -d --build
```

#### 3. Access the application

[`http://localhost:5173`](http://localhost:5173)


## Roadmap

- [x] Foundational architecture
- [x] Transaction logging
- [x] Pin transaction
- [x] Transition to PrimeVue 4
- [x] Account and tag management
- [ ] Transaction overview
    - [ ] Multi-day transactions
    - [ ] Account state tracking
- [ ] Advanced analytics display
- [ ] Household inventory
    - [ ] Stock display and alerts
    - [ ] Food cost and nutrition log
- [ ] ...

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

<!-- URLs -->
[python-shield]: https://img.shields.io/badge/python-3.11-blue?logo=python
[python-url]: https://www.python.org/downloads/release/python-31114/
[fastapi-shield]: https://img.shields.io/badge/FastAPI-009485.svg?logo=fastapi&logoColor=white
[fastapi-url]: https://fastapi.tiangolo.com/
[postgres-shield]: https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white
[postgres-url]: https://www.postgresql.org/
[vue-shield]: https://img.shields.io/badge/Vue.js-3.5-4fc08d?style=flat&logo=vuedotjs
[vue-url]: https://vuejs.org/
[license-shield]: https://img.shields.io/badge/license-MIT-blue
[license-url]: https://github.com/01011001010/Finance-Manager/blob/main/LICENSE
[precommit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit
[precommit-url]: https://pre-commit.com/
[vscode-shield]: https://custom-icon-badges.demolab.com/badge/Visual%20Studio%20Code-0078d7.svg?logo=vsc&logoColor=white
[vscode-url]: https://code.visualstudio.com/
[docker-shield]: https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff
[docker-url]: https://www.docker.com/
[pep8-url]: https://www.python.org/dev/peps/pep-0008/
[pep8-shield]: https://img.shields.io/badge/code_style-pep8-blue
[lifecycle-shield]: https://img.shields.io/badge/Lifecycle-Experimental-orange
