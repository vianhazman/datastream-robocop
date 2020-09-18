## RobocopV2
Listens to Docker container logs and restarts it if certain keyword found. Job configurations are done in .yaml file on the `configs` folder.

### Example Configuration

```
name: Debezium Agent
container: 63f5c4aba332
keyword:
  - org.postgresql.util.PSQLException: Database connection failed when reading from copy.
notification:
  chatID: <telegram_chat_id>
  chatToken: <telegram_chat_token>
```