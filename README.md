# Mugundhan's resume projects

Four independently runnable reference implementations based on the project descriptions in `myresume.pdf`.

| Project | What runs locally | Optional integration |
| --- | --- | --- |
| [Pothole Detection](pothole-detection/README.md) | Video/GPS alignment, deduplication, report JSON | YOLO weights, OpenCV, FastAPI |
| [MentorAI](mentorai/README.md) | Text ingestion, cited answers, browser interface | FastAPI, Docker |
| [Predictive Autoscaler](autoscaler/README.md) | Forecasting, tabular RL, simulation, policy comparison | User supplied traffic CSV |
| [Finance Agent](finance-agent/README.md) | Deterministic paper-trade decisions and audit log | Alpaca paper API, local Ollama rationale |

All examples use synthetic or user supplied inputs. They do not bundle private datasets, trained model weights, cloud accounts, credentials, or unverified accuracy/cost figures. Each README states the prerequisites and the exact command to run. Check `python -m unittest discover -s tests -v` for the dependency free core.
