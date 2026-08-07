import copy
from typing import Set


def optimize_resume(base_resume: dict, jd_keywords: Set[str],
                    job_title: str) -> dict:
    """
    Optimize resume for a specific job by:
    1. Injecting ALL JD keywords into the skills section
    2. Rewriting summary to match job title
    3. Reordering skills to put JD-relevant ones first

    Returns a new optimized resume dict (does not modify original).
    """
    resume = copy.deepcopy(base_resume)

    # --- 1. Inject JD keywords into skills ---
    _inject_keywords(resume, jd_keywords)

    # --- 2. Optimize summary for job title ---
    _optimize_summary(resume, job_title, jd_keywords)

    # --- 3. Reorder skills (JD-relevant first) ---
    _reorder_skills(resume, jd_keywords)

    return resume


def _inject_keywords(resume: dict, jd_keywords: Set[str]):
    """Add JD keywords into appropriate skills categories."""
    skills = resume.get("skills", {})

    # Gather all existing skills (lowercased) for dedup
    existing = set()
    for category, skill_list in skills.items():
        for s in skill_list:
            existing.add(s.lower())

    # Categorize and inject missing keywords
    for kw in jd_keywords:
        if kw in existing:
            continue

        category = _categorize_keyword(kw)
        if category not in skills:
            skills[category] = []
        # Title-case the keyword for display
        skills[category].append(_title_case(kw))
        existing.add(kw)

    resume["skills"] = skills


def _optimize_summary(resume: dict, job_title: str, jd_keywords: Set[str]):
    """Rewrite summary to include job title and top JD keywords."""
    years = resume.get("personal", {}).get("total_experience_years", 2)
    top_keywords = sorted(jd_keywords)[:6]
    keyword_str = ", ".join(_title_case(k) for k in top_keywords)

    summary = (
        f"Backend Software Engineer with {years}+ years of experience "
        f"designing and scaling distributed systems, microservices, and "
        f"high-throughput APIs. "
    )
    if keyword_str:
        summary += f"Proficient in {keyword_str}. "
    summary += (
        f"Proven track record of building reliable, scalable backend "
        f"services, optimizing performance, and shipping production-grade "
        f"software in Agile environments."
    )
    resume["summary"] = summary


def _reorder_skills(resume: dict, jd_keywords: Set[str]):
    """Put JD-relevant skills at the front of each category list."""
    skills = resume.get("skills", {})
    for category, skill_list in skills.items():
        relevant = [s for s in skill_list if s.lower() in jd_keywords]
        others = [s for s in skill_list if s.lower() not in jd_keywords]
        skills[category] = relevant + others
    resume["skills"] = skills


def _categorize_keyword(keyword: str) -> str:
    """Categorize a keyword into the appropriate skills section.

    Categories match resume/base.yaml:
    programming_languages, frameworks, databases, distributed_systems,
    tools, methodologies.
    """
    kw = keyword.lower()

    languages = {"java", "python", "kotlin", "scala", "go", "golang",
                 "c++", "c#", "javascript", "typescript", "ruby", "rust",
                 "groovy", "clojure"}
    if kw in languages:
        return "programming_languages"

    frameworks = {"spring", "spring boot", "spring mvc", "micronaut",
                  "dropwizard", "quarkus", "vertx", "vert.x", "hibernate",
                  "jpa", "django", "flask", "fastapi", "node.js", "nodejs",
                  "express", "ktor", "netty",
                  "rest", "rest api", "restful", "restful apis", "graphql",
                  "grpc", "soap", "websocket", "websockets", "openapi",
                  "swagger", "protobuf", "oauth", "jwt", "api gateway"}
    if kw in frameworks:
        return "frameworks"

    databases = {"sql", "mysql", "postgresql", "postgres", "oracle",
                 "sql server", "mongodb", "cassandra", "dynamodb", "redis",
                 "memcached", "elasticsearch", "solr", "neo4j", "hbase",
                 "couchbase", "firebase", "nosql", "rdbms", "aerospike",
                 "clickhouse", "snowflake"}
    if kw in databases:
        return "databases"

    distributed = {"microservices", "distributed systems", "system design",
                   "scalability", "high availability", "fault tolerance",
                   "sharding", "partitioning", "replication", "consistency",
                   "caching", "load balancing", "consensus", "concurrency",
                   "multithreading", "asynchronous", "scatter-gather",
                   "cap theorem", "idempotency", "rate limiting",
                   "kafka", "rabbitmq", "activemq", "pulsar", "sqs", "sns",
                   "kinesis", "event-driven", "event driven", "pub/sub",
                   "pubsub", "message queue",
                   "spark", "hadoop", "flink", "airflow", "hive", "presto",
                   "storm", "beam", "etl", "data pipeline"}
    if kw in distributed:
        return "distributed_systems"

    tools = {"aws", "azure", "gcp", "google cloud", "docker", "kubernetes",
             "k8s", "terraform", "ansible", "helm", "jenkins", "ci/cd",
             "ci cd", "github actions", "gitlab ci", "circleci", "argocd",
             "prometheus", "grafana", "datadog", "splunk", "elk", "kibana",
             "new relic", "ec2", "s3", "lambda", "ecs", "eks",
             "cloudformation", "git", "github", "gitlab", "bitbucket",
             "maven", "gradle", "jira", "junit", "testng", "mockito",
             "pytest", "sonarqube"}
    if kw in tools:
        return "tools"

    methodologies = {"agile", "scrum", "kanban", "tdd", "bdd", "oop",
                     "design patterns", "data structures", "algorithms",
                     "solid", "domain-driven design", "ddd",
                     "clean architecture"}
    if kw in methodologies:
        return "methodologies"

    # Default bucket for anything uncategorized
    return "tools"


def _title_case(keyword: str) -> str:
    """Smart title-case for technical terms."""
    special_cases = {
        "ci/cd": "CI/CD", "ci cd": "CI/CD", "bdd": "BDD", "tdd": "TDD",
        "oop": "OOP", "ddd": "DDD", "solid": "SOLID",
        "rest": "REST", "rest api": "REST API", "restful": "RESTful",
        "restful apis": "RESTful APIs", "graphql": "GraphQL", "grpc": "gRPC",
        "soap": "SOAP", "api gateway": "API Gateway", "jwt": "JWT",
        "oauth": "OAuth", "openapi": "OpenAPI", "json": "JSON", "xml": "XML",
        "sql": "SQL", "mysql": "MySQL", "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL", "sql server": "SQL Server",
        "mongodb": "MongoDB", "dynamodb": "DynamoDB", "nosql": "NoSQL",
        "rdbms": "RDBMS", "hbase": "HBase", "clickhouse": "ClickHouse",
        "aws": "AWS", "gcp": "GCP", "google cloud": "Google Cloud",
        "k8s": "K8s", "kubernetes": "Kubernetes", "ec2": "EC2", "s3": "S3",
        "ecs": "ECS", "eks": "EKS", "sqs": "SQS", "sns": "SNS",
        "github": "GitHub", "gitlab": "GitLab", "gitlab ci": "GitLab CI",
        "bitbucket": "Bitbucket", "github actions": "GitHub Actions",
        "circleci": "CircleCI", "argocd": "ArgoCD", "elk": "ELK",
        "etl": "ETL", "cap theorem": "CAP Theorem", "vert.x": "Vert.x",
        "vertx": "Vert.x", "node.js": "Node.js", "nodejs": "Node.js",
        "fastapi": "FastAPI", "jpa": "JPA", "junit": "JUnit",
        "testng": "TestNG", "golang": "Go", "c++": "C++", "c#": "C#",
        "typescript": "TypeScript", "javascript": "JavaScript",
        "spring boot": "Spring Boot", "spring mvc": "Spring MVC",
        "pub/sub": "Pub/Sub", "pubsub": "Pub/Sub", "activemq": "ActiveMQ",
        "rabbitmq": "RabbitMQ", "event-driven": "Event-Driven",
        "event driven": "Event-Driven", "domain-driven design":
        "Domain-Driven Design", "scatter-gather": "Scatter-Gather",
        "new relic": "New Relic", "sonarqube": "SonarQube",
        "high availability": "High Availability",
        "fault tolerance": "Fault Tolerance", "system design": "System Design",
        "distributed systems": "Distributed Systems",
        "load balancing": "Load Balancing", "rate limiting": "Rate Limiting",
        "message queue": "Message Queue", "data pipeline": "Data Pipeline",
        "data structures": "Data Structures", "design patterns":
        "Design Patterns", "clean architecture": "Clean Architecture",
    }
    if keyword.lower() in special_cases:
        return special_cases[keyword.lower()]
    return keyword.title()
