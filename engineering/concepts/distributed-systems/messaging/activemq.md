# ActiveMQ

Apache ActiveMQ is a traditional, JMS-based (Java Message Service) message broker — one of the older, still-common options predating [RabbitMQ](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md) and [Kafka](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md), still widely deployed in enterprise/JVM-heavy environments (banking, government, large legacy systems).

## JMS: The Standard Underneath It

Unlike [RabbitMQ](rabbitmq.md) (which speaks AMQP) or [Kafka](kafka.md) (its own custom protocol), ActiveMQ's primary API is **JMS** — a Java standard interface for messaging that multiple broker vendors implement, similar in spirit to how JDBC is a standard interface multiple databases implement. This means Java/JVM application code written against the JMS interface can, in principle, switch underlying brokers with less code change than switching between non-standardized APIs.

```java
ConnectionFactory factory = new ActiveMQConnectionFactory("tcp://localhost:61616");
Connection connection = factory.createConnection();
Session session = connection.createSession(false, Session.AUTO_ACKNOWLEDGE);

Queue queue = session.createQueue("orders");
MessageProducer producer = session.createProducer(queue);
producer.send(session.createTextMessage("{\"orderId\": 123}"));
```

## Queue vs. Topic (JMS Model)

| Model | Delivery |
|---|---|
| **Queue** | Point-to-point — one message, consumed by exactly one consumer among any listening |
| **Topic** | [Publish-subscribe](publish-subscribe.md) — one message, delivered to every currently-subscribed consumer |

This queue/topic split is the same fan-out-vs-point-to-point distinction seen across nearly every broker in this vault ([RabbitMQ](rabbitmq.md) exchanges, [Azure Service Bus](azure-service-bus.md) queues/topics) — JMS just standardizes the vocabulary for it across Java brokers specifically.

## ActiveMQ Classic vs. ActiveMQ Artemis

Apache maintains two versions: **ActiveMQ Classic** (the original, mature, JMS 1.1-focused implementation) and **ActiveMQ Artemis** (a newer core, better performance, broader protocol support including AMQP and MQTT alongside JMS) — Artemis is the actively-recommended choice for new deployments, with Classic maintained mainly for existing installations.

## Common Questions

**Why would a new project choose ActiveMQ over [RabbitMQ](rabbitmq.md) or [Kafka](kafka.md) today?**
> Mainly when the surrounding ecosystem is already JVM/JMS-based (an existing Java Enterprise codebase, other JMS-dependent tooling) — for a greenfield system with no such constraint, [RabbitMQ](rabbitmq.md) or [Kafka](kafka.md) are more commonly recommended today, with ActiveMQ (specifically Artemis) as a reasonable choice when JMS compatibility itself is a requirement.

**Is JMS itself a broker?**
> No — JMS is just the API specification; ActiveMQ, and other brokers like IBM MQ, are implementations of it. This is the same relationship as JDBC (interface) to [PostgreSQL](../../databases/relational/postgresql.md)/[MySQL](../../databases/relational/mysql.md) (implementations).

## Related

- [Message Brokers: Kafka, RabbitMQ, SQS](../../../overviews/distributed-systems/message-brokers-kafka-rabbitmq-sqs.md)
- [ZeroMQ](zeromq.md)
- [Azure Service Bus](azure-service-bus.md)
