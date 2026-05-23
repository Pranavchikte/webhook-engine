- Used async SQLAlchemy engine because FastAPI is async — 
  blocking DB calls would kill concurrency
- Connection pool set to 10+20 to handle burst traffic 
  without overwhelming PostgreSQL
- UUID PKs over integer IDs — prevents enumeration attacks 
  and works across distributed systems
- Delivery model tracks retry state directly — 
  avoids separate retry queue table
- task_acks_late=True: ensures no delivery is lost 
  if worker crashes mid-execution
- prefetch_multiplier=1: fair task distribution 
  across multiple workers
- Exponential backoff mirrors Stripe's webhook retry pattern
- DEAD status after 5 retries — prevents infinite retry loops
  hammering a dead endpoint
- httpx timeout=10s — industry standard for webhook delivery
- HMAC-SHA256 for signing — same approach used by Stripe, 
  GitHub webhooks
- compare_digest over == operator — prevents timing attacks
- JSON structured logging — production systems ship logs 
  to aggregators like Datadog, plain text logs are unsearchable
- Metrics endpoint exposes delivery health in real time
- success_rate calculated server side — 
  monitoring tools just scrape this endpoint
- Celery task dispatched after DB commit — 
  worker always finds the delivery record in DB
- Pass only IDs to Celery tasks — 
  full objects cause serialization issues