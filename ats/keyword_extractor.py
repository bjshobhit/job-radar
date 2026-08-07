import re
from typing import Set

# Master keyword dictionary — common backend / distributed-systems keywords
# to look for in job descriptions.
KEYWORD_BANK = {
    # Programming languages
    "java", "python", "kotlin", "scala", "go", "golang", "c++", "c#",
    "javascript", "typescript", "ruby", "rust", "groovy", "clojure",
    # Frameworks & web
    "spring", "spring boot", "spring mvc", "micronaut", "dropwizard",
    "quarkus", "vertx", "vert.x", "hibernate", "jpa", "django", "flask",
    "fastapi", "node.js", "nodejs", "express", "ktor", "netty",
    # APIs & protocols
    "rest", "rest api", "restful", "restful apis", "graphql", "grpc",
    "soap", "websocket", "websockets", "openapi", "swagger", "protobuf",
    "json", "xml", "oauth", "jwt", "api gateway",
    # Messaging & streaming
    "kafka", "rabbitmq", "activemq", "pulsar", "sqs", "sns", "kinesis",
    "event-driven", "event driven", "pub/sub", "pubsub", "message queue",
    # Databases & storage
    "sql", "mysql", "postgresql", "postgres", "oracle", "sql server",
    "mongodb", "cassandra", "dynamodb", "redis", "memcached",
    "elasticsearch", "solr", "neo4j", "hbase", "couchbase", "firebase",
    "nosql", "rdbms", "aerospike", "clickhouse", "snowflake",
    # Distributed systems & concepts
    "microservices", "distributed systems", "system design", "scalability",
    "high availability", "fault tolerance", "sharding", "partitioning",
    "replication", "consistency", "caching", "load balancing",
    "consensus", "concurrency", "multithreading", "asynchronous",
    "scatter-gather", "cap theorem", "idempotency", "rate limiting",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "helm", "jenkins", "ci/cd", "ci cd",
    "github actions", "gitlab ci", "circleci", "argocd", "prometheus",
    "grafana", "datadog", "splunk", "elk", "kibana", "new relic",
    "ec2", "s3", "lambda", "ecs", "eks", "cloudformation",
    # Big data & processing
    "spark", "hadoop", "flink", "airflow", "hive", "presto", "storm",
    "beam", "etl", "data pipeline",
    # Tools & build
    "git", "github", "gitlab", "bitbucket", "maven", "gradle", "jira",
    "junit", "testng", "mockito", "pytest", "sonarqube",
    # Methodologies
    "agile", "scrum", "kanban", "tdd", "bdd", "oop",
    "design patterns", "data structures", "algorithms", "solid",
    "domain-driven design", "ddd", "clean architecture",
}


def extract_keywords(jd_text: str) -> Set[str]:
    """
    Extract relevant technical keywords from a job description.
    Returns a set of matched keywords (lowercased).
    """
    if not jd_text:
        return set()

    text = jd_text.lower()
    found = set()

    for keyword in KEYWORD_BANK:
        # Use word boundary matching for short keywords to avoid false positives
        if len(keyword) <= 3:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, text):
                found.add(keyword)
        else:
            if keyword in text:
                found.add(keyword)

    return found


def get_resume_keywords(resume_data: dict) -> Set[str]:
    """
    Extract all keywords present in the resume data.
    Collects from skills, experience bullets, projects, and summary.
    """
    text_parts = []

    # Summary
    if resume_data.get("summary"):
        text_parts.append(resume_data["summary"])

    # Skills sections
    skills = resume_data.get("skills", {})
    for category, skill_list in skills.items():
        if isinstance(skill_list, list):
            text_parts.extend(skill_list)

    # Experience bullets
    for exp in resume_data.get("experience", []):
        for bullet in exp.get("bullets", []):
            text_parts.append(bullet)

    # Project bullets
    for proj in resume_data.get("projects", []):
        for bullet in proj.get("bullets", []):
            text_parts.append(bullet)

    full_text = " ".join(text_parts).lower()
    found = set()

    for keyword in KEYWORD_BANK:
        if len(keyword) <= 3:
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, full_text):
                found.add(keyword)
        else:
            if keyword in full_text:
                found.add(keyword)

    return found
