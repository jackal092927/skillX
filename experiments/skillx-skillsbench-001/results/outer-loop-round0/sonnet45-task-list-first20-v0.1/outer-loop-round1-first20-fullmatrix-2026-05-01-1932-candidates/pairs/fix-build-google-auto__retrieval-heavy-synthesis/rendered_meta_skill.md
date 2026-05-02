[Common wrapper]
You are revising a Task skill, not directly solving the task.
Use the provided Meta schema as class-level guidance.
Your goal is to improve the Task skill for this task while preserving useful existing structure.

[Meta schema block]
Category: retrieval-heavy-synthesis
Semantic intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.
Emphasize:
- retrieval plan that explicitly identifies external sources and access paths before processing
- evidence tracking with explicit provenance chains linking each claim to its supporting external source
- compression that preserves source citations and provenance chains alongside synthesized output
- abstain / unknown behavior when evidence is insufficient
- external source grounding discipline - explicitly identify and track which external source (file, API, database, document) supports each claim
- explicit provenance chains - maintain traceable mappings from output claims back to specific input evidence locations
- multi-source reconciliation - handle conflicting or partial evidence across multiple external sources with explicit conflict resolution
Avoid:
- unsupported synthesis
- hallucinated joins across sources
- excessive workflow scaffolding that obscures evidence use
- treating staged data processing as retrieval-synthesis when the task does not require external source provenance tracking
Expected good fit:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
- tasks requiring multi-source evidence reconciliation with explicit provenance tracking
Expected bad fit:
- simulator/control tasks
- code patch workflows
- staged multi-step data processing pipelines without explicit external source grounding requirements
- tasks where the primary challenge is workflow orchestration rather than evidence provenance discipline
Hypothesized primary failure modes:
- unavailable in prompt-bank-v0.1; use task-local evidence instead
Meta schema seed guidance:
You are revising a skill for a retrieval-heavy-synthesis task.
Schema intent: Gather evidence from sources, compress it correctly, and synthesize an output without dropping support.

Outer-loop update mode: differentiating. Keep the Render layer fixed and change only schema-level guidance.

Prioritize:
1. retrieval plan that explicitly identifies external sources and access paths before processing
2. evidence tracking with explicit provenance chains linking each claim to its supporting external source
3. compression that preserves source citations and provenance chains alongside synthesized output
4. abstain / unknown behavior when evidence is insufficient
5. external source grounding discipline - explicitly identify and track which external source (file, API, database, document) supports each claim
6. explicit provenance chains - maintain traceable mappings from output claims back to specific input evidence locations
7. multi-source reconciliation - handle conflicting or partial evidence across multiple external sources with explicit conflict resolution

Avoid:
1. unsupported synthesis
2. hallucinated joins across sources
3. excessive workflow scaffolding that obscures evidence use
4. treating staged data processing as retrieval-synthesis when the task does not require external source provenance tracking

Good fit when:
- information search
- handbook / database grounded QA
- report or answer generation from external sources
- tasks requiring multi-source evidence reconciliation with explicit provenance tracking

Bad fit when:
- simulator/control tasks
- code patch workflows
- staged multi-step data processing pipelines without explicit external source grounding requirements
- tasks where the primary challenge is workflow orchestration rather than evidence provenance discipline

Primary failure modes to guard against:
- boundary ambiguity with analytic-pipeline on tasks that process data but don't require external source provenance tracking
- schema assignment to pipeline-pattern tasks that lack load-bearing evidence grounding requirements

Regenerate task-specific skill guidance from these slots; do not invent a new policy outside them.

[Task context block]
Task name: fix-build-google-auto
Task summary: You need to fix build errors in a Java codebase. The repository is located in `/home/travis/build/failed/<repo>/<id>`.
Task constraints:
- seed schema prior: engineering-composition
- verifier mode: benchmark-threshold
- workflow topology: staged-multi-step
- tool surface regime: tool-heavy-script-recommended
- primary pattern: pipeline
- annotation confidence: high
- secondary patterns: reviewer, tool-wrapper
Task output requirements:
- verifier note: benchmark-threshold
- current skill count: 3

[Current Task skill block]
Current Task skill:
## maven-build-lifecycle
---
name: maven-build-lifecycle
description: Use when working with Maven build phases, goals, profiles, or customizing the build process for Java projects.
---

# Maven Build Lifecycle

Master Maven's build lifecycle including phases, goals, profiles, and build customization for efficient Java project builds.

## Overview

Maven's build lifecycle is a well-defined sequence of phases that execute in order. Understanding the lifecycle is essential for effective build configuration and optimization.

## Default Lifecycle Phases

### Complete Phase Order

```
1.  validate      - Validate project structure
2.  initialize    - Initialize build state
3.  generate-sources
4.  process-sources
5.  generate-resources
6.  process-resources - Copy resources to output
7.  compile       - Compile source code
8.  process-classes
9.  generate-test-sources
10. process-test-sources
11. generate-test-resources
12. process-test-resources
13. test-compile  - Compile test sources
14. process-test-classes
15. test          - Run unit tests
16. prepare-package
17. package       - Create JAR/WAR
18. pre-integration-test
19. integration-test - Run integration tests
20. post-integration-test
21. verify        - Run verification checks
22. install       - Install to local repo
23. deploy        - Deploy to remote repo
```

### Common Phase Commands

```bash
# Compile only
mvn compile

# Compile and run tests
mvn test

# Create package
mvn package

# Install to local repository
mvn install

# Deploy to remote repository
mvn deploy

# Clean and build
mvn clean install

# Skip tests
mvn install -DskipTests

# Skip test compilation and execution
mvn install -Dmaven.test.skip=true
```

## Clean Lifecycle

```
1. pre-clean
2. clean         - Delete target directory
3. post-clean
```

```bash
# Clean build artifacts
mvn clean

# Clean specific directory
mvn clean -DbuildDirectory=out
```

## Site Lifecycle

```
1. pre-site
2. site          - Generate documentation
3. post-site
4. site-deploy   - Deploy documentation
```

```bash
# Generate site
mvn site

# Generate and deploy site
mvn site-deploy
```

## Goals vs Phases

### Executing Phases

```bash
# Execute phase (runs all previous phases)
mvn package
```

### Executing Goals

```bash
# Execute specific goal
mvn compiler:compile
mvn surefire:test
mvn jar:jar

# Multiple goals
mvn dependency:tree compiler:compile
```

### Phase-to-Goal Bindings

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.12.1</version>
            <executions>
                <execution>
                    <id>compile-sources</id>
                    <phase>compile</phase>
                    <goals>
                        <goal>compile</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

## Build Profiles

### Profile Definition

```xml
<profiles>
    <profile>
        <id>development</id>
        <activation>
            <activeByDefault>true</activeByDefault>
        </activation>
        <properties>
            <env>dev</env>
            <skip.integration.tests>true</skip.integration.tests>
        </properties>
    </profile>

    <profile>
        <id>production</id>
        <properties>
            <env>prod</env>
            <skip.integration.tests>false</skip.integration.tests>
        </properties>
        <build>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <configuration>
                        <debug>false</debug>
                        <optimize>true</optimize>
                    </configuration>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

### Profile Activation

```bash
# Activate by name
mvn install -Pproduction

# Multiple profiles
mvn install -Pproduction,ci

# Deactivate profile
mvn install -P!development
```

### Activation Triggers

```xml
<profile>
    <id>jdk17</id>
    <activation>
        <!-- Activate by JDK version -->
        <jdk>17</jdk>
    </activation>
</profile>

<profile>
    <id>windows</id>
    <activation>
        <!-- Activate by OS -->
        <os>
            <family>windows</family>
        </os>
    </activation>
</profile>

<profile>
    <id>ci</id>
    <activation>
        <!-- Activate by environment variable -->
        <property>
            <name>env.CI</name>
            <value>true</value>
        </property>
    </activation>
</profile>

<profile>
    <id>with-config</id>
    <activation>
        <!-- Activate by file existence -->
        <file>
            <exists>src/main/config/app.properties</exists>
        </file>
    </activation>
</profile>
```

## Resource Filtering

### Enable Filtering

```xml
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>true</filtering>
            <includes>
                <include>**/*.properties</include>
                <include>**/*.xml</include>
            </includes>
        </resource>
        <resource>
            <directory>src/main/resources</directory>
            <filtering>false</filtering>
            <excludes>
                <exclude>**/*.properties</exclude>
                <exclude>**/*.xml</exclude>
            </excludes>
        </resource>
    </resources>
</build>
```

### Property Substitution

```properties
# application.properties
app.name=${project.name}
app.version=${project.version}
app.environment=${env}
build.timestamp=${maven.build.timestamp}
```

## Build Customization

### Source and Target Configuration

```xml
<properties>
    <maven.compiler.source>17</maven.compiler.source>
    <maven.compiler.target>17</maven.compiler.target>
    <maven.compiler.release>17</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
```

### Custom Source Directories

```xml
<build>
    <sourceDirectory>src/main/java</sourceDirectory>
    <testSourceDirectory>src/test/java</testSourceDirectory>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
        </resource>
    </resources>
    <testResources>
        <testResource>
            <directory>src/test/resources</directory>
        </testResource>
    </testResources>
</build>
```

### Final Name and Output

```xml
<build>
    <finalName>${project.artifactId}-${project.version}</finalName>
    <directory>target</directory>
    <outputDirectory>target/classes</outputDirectory>
    <testOutputDirectory>target/test-classes</testOutputDirectory>
</build>
```

## Multi-Module Builds

### Reactor Options

```bash
# Build all modules
mvn install

# Build specific module and dependencies
mvn install -pl module-name -am

# Build dependents of a module
mvn install -pl module-name -amd

# Resume from specific module
mvn install -rf :module-name

# Build in parallel
mvn install -T 4
mvn install -T 1C  # 1 thread per CPU core
```

### Module Order Control

```xml
<!-- parent/pom.xml -->
<modules>
    <module>common</module>
    <module>api</module>
    <module>service</module>
    <module>web</module>
</modules>
```

## Test Configuration

### Surefire Plugin (Unit Tests)

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.3</version>
    <configuration>
        <includes>
            <include>**/*Test.java</include>
            <include>**/*Tests.java</include>
        </includes>
        <excludes>
            <exclude>**/*IntegrationTest.java</exclude>
        </excludes>
        <parallel>methods</parallel>
        <threadCount>4</threadCount>
        <forkCount>1</forkCount>
        <reuseForks>true</reuseForks>
    </configuration>
</plugin>
```

### Failsafe Plugin (Integration Tests)

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-failsafe-plugin</artifactId>
    <version>3.2.3</version>
    <executions>
        <execution>
            <goals>
                <goal>integration-test</goal>
                <goal>verify</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <includes>
            <include>**/*IT.java</include>
            <include>**/*IntegrationTest.java</include>
        </includes>
    </configuration>
</plugin>
```

## Build Optimization

### Incremental Builds

```bash
# Skip unchanged modules
mvn install -amd

# Use build cache (requires Maven Daemon)
mvnd install
```

### Parallel Builds

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <configuration>
                <fork>true</fork>
                <compilerArgs>
                    <arg>-J-Xmx512m</arg>
                </compilerArgs>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### Build Cache

```bash
# Enable build cache (Maven 4+)
mvn install -Dmaven.build.cache.enabled=true
```

## Debugging Builds

### Verbose Output

```bash
# Debug mode
mvn install -X

# Error stacktrace
mvn install -e

# Quiet mode
mvn install -q
```

### Effective POM

```bash
# View resolved POM
mvn help:effective-pom

# View effective settings
mvn help:effective-settings

# Active profiles
mvn help:active-profiles
```

### Dependency Analysis

```bash
# Check plugin versions
mvn versions:display-plugin-updates

# Check dependency versions
mvn versions:display-dependency-updates
```

## Best Practices

1. **Use Clean Builds** - Run `mvn clean` before releases
2. **Consistent Versions** - Lock plugin versions
3. **Profile Isolation** - Keep profiles focused
4. **Fail Fast** - Use `-ff` in CI for quick feedback
5. **Parallel Builds** - Use `-T` for multi-module projects
6. **Skip Wisely** - Know the difference between skip options
7. **Resource Filtering** - Enable only where needed
8. **Test Separation** - Unit tests in Surefire, integration in Failsafe
9. **Reproducible Builds** - Pin all plugin versions
10. **Document Profiles** - Comment profile purposes

## Common Pitfalls

1. **Skipping Tests** - Don't skip tests in CI
2. **SNAPSHOT in Release** - Remove snapshots before release
3. **Missing Clean** - Stale files causing issues
4. **Profile Conflicts** - Overlapping profile configurations
5. **Resource Filtering** - Accidentally filtering binaries
6. **Phase Confusion** - Running wrong phase
7. **Memory Issues** - Insufficient heap for large builds
8. **Reactor Order** - Module dependency issues

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build with Maven
  run: mvn -B clean verify -Pci

- name: Release
  run: mvn -B deploy -Prelease -DskipTests
```

### Jenkins Pipeline

```groovy
stage('Build') {
    steps {
        sh 'mvn -B clean package -DskipTests'
    }
}
stage('Test') {
    steps {
        sh 'mvn -B test'
    }
}
stage('Integration Test') {
    steps {
        sh 'mvn -B verify -DskipUnitTests'
    }
}
```

## When to Use This Skill

- Setting up new Maven projects
- Customizing build phases
- Creating build profiles for environments
- Configuring test execution
- Optimizing build performance
- Debugging build failures
- Setting up CI/CD pipelines
- Multi-module project configuration

## maven-dependency-management
---
name: maven-dependency-management
description: Use when managing Maven dependencies, resolving dependency conflicts, configuring BOMs, or optimizing dependency trees in Java projects.
---

# Maven Dependency Management

Master Maven dependency management including dependency declaration, scope management, version resolution, BOMs, and dependency tree optimization.

## Overview

Maven's dependency management is a cornerstone of Java project build systems. It handles transitive dependencies, version conflicts, and provides mechanisms for controlling dependency resolution across multi-module projects.

## Dependency Declaration

### Basic Dependency

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.2.0</version>
</dependency>
```

### Dependency with Scope

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.1</version>
    <scope>test</scope>
</dependency>
```

### Optional Dependencies

```xml
<dependency>
    <groupId>com.google.code.findbugs</groupId>
    <artifactId>jsr305</artifactId>
    <version>3.0.2</version>
    <optional>true</optional>
</dependency>
```

## Dependency Scopes

### Available Scopes

| Scope | Compile CP | Test CP | Runtime CP | Transitive |
|-------|-----------|---------|------------|------------|
| compile | Yes | Yes | Yes | Yes |
| provided | Yes | Yes | No | No |
| runtime | No | Yes | Yes | Yes |
| test | No | Yes | No | No |
| system | Yes | Yes | No | No |
| import | N/A | N/A | N/A | N/A |

### Scope Examples

```xml
<!-- Compile scope (default) - available everywhere -->
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-lang3</artifactId>
    <version>3.14.0</version>
</dependency>

<!-- Provided - available at compile, not packaged -->
<dependency>
    <groupId>jakarta.servlet</groupId>
    <artifactId>jakarta.servlet-api</artifactId>
    <version>6.0.0</version>
    <scope>provided</scope>
</dependency>

<!-- Runtime - only needed at runtime -->
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.7.1</version>
    <scope>runtime</scope>
</dependency>

<!-- Test - only for testing -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>5.8.0</version>
    <scope>test</scope>
</dependency>
```

## Version Management

### Property-Based Versions

```xml
<properties>
    <spring-boot.version>3.2.0</spring-boot.version>
    <junit.version>5.10.1</junit.version>
    <jackson.version>2.16.0</jackson.version>
</properties>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <version>${spring-boot.version}</version>
    </dependency>
</dependencies>
```

### Version Ranges

```xml
<!-- Exact version -->
<version>1.0.0</version>

<!-- Greater than or equal -->
<version>[1.0.0,)</version>

<!-- Less than -->
<version>(,1.0.0)</version>

<!-- Range inclusive -->
<version>[1.0.0,2.0.0]</version>

<!-- Range exclusive -->
<version>(1.0.0,2.0.0)</version>
```

### Latest Version (Not Recommended)

```xml
<!-- Avoid in production -->
<version>LATEST</version>
<version>RELEASE</version>
```

## Dependency Management Section

### Centralizing Versions

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.2.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson</groupId>
            <artifactId>jackson-bom</artifactId>
            <version>2.16.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<!-- No version needed when declared in dependencyManagement -->
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
    </dependency>
</dependencies>
```

### BOM (Bill of Materials) Import

```xml
<dependencyManagement>
    <dependencies>
        <!-- Spring Boot BOM -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-dependencies</artifactId>
            <version>3.2.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>

        <!-- AWS SDK BOM -->
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>bom</artifactId>
            <version>2.23.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>

        <!-- JUnit BOM -->
        <dependency>
            <groupId>org.junit</groupId>
            <artifactId>junit-bom</artifactId>
            <version>5.10.1</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## Exclusions

### Excluding Transitive Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-tomcat</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- Add alternative -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jetty</artifactId>
</dependency>
```

### Excluding Logging Frameworks

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter</artifactId>
    <exclusions>
        <exclusion>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-logging</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-log4j2</artifactId>
</dependency>
```

## Dependency Analysis

### View Dependency Tree

```bash
# Full dependency tree
mvn dependency:tree

# Filter by artifact
mvn dependency:tree -Dincludes=org.slf4j

# Output to file
mvn dependency:tree -DoutputFile=deps.txt

# Verbose output showing conflict resolution
mvn dependency:tree -Dverbose
```

### Analyze Dependencies

```bash
# Find unused declared and used undeclared dependencies
mvn dependency:analyze

# Show only problems
mvn dependency:analyze-only

# Include test scope
mvn dependency:analyze -DignoreNonCompile=false
```

### List Dependencies

```bash
# List all dependencies
mvn dependency:list

# List with scope
mvn dependency:list -DincludeScope=runtime
```

## Conflict Resolution

### Maven's Default Strategy

Maven uses "nearest definition wins" for version conflicts:

```
A -> B -> C 1.0
A -> C 2.0
```

Result: C 2.0 is used (nearest to root)

### Forcing Versions

```xml
<dependencyManagement>
    <dependencies>
        <!-- Force specific version across all modules -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>2.0.9</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### Enforcer Plugin for Version Control

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-enforcer-plugin</artifactId>
            <version>3.4.1</version>
            <executions>
                <execution>
                    <id>enforce</id>
                    <goals>
                        <goal>enforce</goal>
                    </goals>
                    <configuration>
                        <rules>
                            <dependencyConvergence/>
                            <requireUpperBoundDeps/>
                            <banDuplicatePomDependencyVersions/>
                        </rules>
                    </configuration>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

## Multi-Module Projects

### Parent POM Dependency Management

```xml
<!-- parent/pom.xml -->
<project>
    <groupId>com.example</groupId>
    <artifactId>parent</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.example</groupId>
                <artifactId>common</artifactId>
                <version>${project.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>

<!-- module/pom.xml -->
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>module</artifactId>

    <dependencies>
        <!-- Version inherited from parent -->
        <dependency>
            <groupId>com.example</groupId>
            <artifactId>common</artifactId>
        </dependency>
    </dependencies>
</project>
```

## Repository Configuration

### Central Repository

```xml
<repositories>
    <repository>
        <id>central</id>
        <url>https://repo.maven.apache.org/maven2</url>
    </repository>
</repositories>
```

### Private Repository

```xml
<repositories>
    <repository>
        <id>company-repo</id>
        <url>https://nexus.company.com/repository/maven-public</url>
        <releases>
            <enabled>true</enabled>
        </releases>
        <snapshots>
            <enabled>true</enabled>
        </snapshots>
    </repository>
</repositories>
```

### Repository in Settings.xml

```xml
<!-- ~/.m2/settings.xml -->
<settings>
    <servers>
        <server>
            <id>company-repo</id>
            <username>${env.REPO_USER}</username>
            <password>${env.REPO_PASS}</password>
        </server>
    </servers>
</settings>
```

## Best Practices

1. **Use dependencyManagement** - Centralize versions in parent POMs
2. **Import BOMs** - Use well-maintained BOMs for framework dependencies
3. **Avoid Version Ranges** - Pin exact versions for reproducibility
4. **Regular Updates** - Keep dependencies current for security
5. **Minimize Scopes** - Use appropriate scopes to reduce package size
6. **Exclude Unused** - Remove unused transitive dependencies
7. **Document Exclusions** - Comment why exclusions are needed
8. **Run dependency:analyze** - Regularly check for issues
9. **Use Enforcer Plugin** - Ensure dependency convergence
10. **Lock Versions** - Use versions-maven-plugin for updates

## Common Pitfalls

1. **Version Conflicts** - Transitive dependency version mismatches
2. **Missing Exclusions** - Duplicate classes from different artifacts
3. **Wrong Scope** - Compile vs runtime vs provided confusion
4. **Outdated Dependencies** - Security vulnerabilities in old versions
5. **Circular Dependencies** - Module A depends on B depends on A
6. **Snapshot in Production** - Using SNAPSHOT versions in releases
7. **System Scope** - Hardcoded paths break portability
8. **Optional Misuse** - Marking required dependencies as optional

## Troubleshooting

### Debug Dependency Resolution

```bash
# Enable debug output
mvn dependency:tree -X

# Show conflict resolution
mvn dependency:tree -Dverbose=true
```

### Force Re-download

```bash
# Clear local repository cache
mvn dependency:purge-local-repository

# Force update
mvn -U clean install
```

### Check Effective POM

```bash
# See resolved dependency versions
mvn help:effective-pom
```

## When to Use This Skill

- Adding new dependencies to a project
- Resolving version conflicts
- Setting up multi-module project dependencies
- Configuring BOM imports
- Optimizing dependency trees
- Troubleshooting classpath issues
- Upgrading dependency versions
- Excluding problematic transitive dependencies

## maven-plugin-configuration
---
name: maven-plugin-configuration
description: Use when configuring Maven plugins, setting up common plugins like compiler, surefire, jar, or creating custom plugin executions.
---

# Maven Plugin Configuration

Master Maven plugin configuration including core plugins, build plugins, reporting plugins, and custom plugin development.

## Overview

Maven plugins provide the actual functionality for building projects. Understanding how to configure plugins effectively is essential for customizing builds, optimizing performance, and ensuring code quality.

## Plugin Basics

### Plugin Structure

```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.12.1</version>
            <configuration>
                <!-- Plugin-specific configuration -->
            </configuration>
            <executions>
                <execution>
                    <id>compile-java</id>
                    <phase>compile</phase>
                    <goals>
                        <goal>compile</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

### Plugin Management

```xml
<build>
    <pluginManagement>
        <plugins>
            <!-- Define versions and shared config -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.12.1</version>
                <configuration>
                    <release>17</release>
                </configuration>
            </plugin>
        </plugins>
    </pluginManagement>
    <plugins>
        <!-- Actually use plugin (inherits config) -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
        </plugin>
    </plugins>
</build>
```

## Core Build Plugins

### Compiler Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.12.1</version>
    <configuration>
        <release>17</release>
        <encoding>UTF-8</encoding>
        <showWarnings>true</showWarnings>
        <showDeprecation>true</showDeprecation>
        <compilerArgs>
            <arg>-Xlint:all</arg>
            <arg>-parameters</arg>
        </compilerArgs>
        <annotationProcessorPaths>
            <path>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>1.18.30</version>
            </path>
        </annotationProcessorPaths>
    </configuration>
</plugin>
```

### Resources Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-resources-plugin</artifactId>
    <version>3.3.1</version>
    <configuration>
        <encoding>UTF-8</encoding>
        <propertiesEncoding>UTF-8</propertiesEncoding>
        <nonFilteredFileExtensions>
            <nonFilteredFileExtension>pdf</nonFilteredFileExtension>
            <nonFilteredFileExtension>ico</nonFilteredFileExtension>
            <nonFilteredFileExtension>png</nonFilteredFileExtension>
            <nonFilteredFileExtension>jpg</nonFilteredFileExtension>
        </nonFilteredFileExtensions>
    </configuration>
</plugin>
```

### JAR Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-jar-plugin</artifactId>
    <version>3.3.0</version>
    <configuration>
        <archive>
            <manifest>
                <addClasspath>true</addClasspath>
                <mainClass>com.example.Main</mainClass>
                <addDefaultImplementationEntries>true</addDefaultImplementationEntries>
                <addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
            </manifest>
            <manifestEntries>
                <Build-Time>${maven.build.timestamp}</Build-Time>
                <Built-By>${user.name}</Built-By>
            </manifestEntries>
        </archive>
        <excludes>
            <exclude>**/logback-test.xml</exclude>
        </excludes>
    </configuration>
    <executions>
        <execution>
            <id>test-jar</id>
            <goals>
                <goal>test-jar</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### Source Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-source-plugin</artifactId>
    <version>3.3.0</version>
    <executions>
        <execution>
            <id>attach-sources</id>
            <goals>
                <goal>jar-no-fork</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### Javadoc Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-javadoc-plugin</artifactId>
    <version>3.6.3</version>
    <configuration>
        <doclint>none</doclint>
        <source>17</source>
        <quiet>true</quiet>
        <links>
            <link>https://docs.oracle.com/en/java/javase/17/docs/api/</link>
        </links>
    </configuration>
    <executions>
        <execution>
            <id>attach-javadocs</id>
            <goals>
                <goal>jar</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## Testing Plugins

### Surefire Plugin (Unit Tests)

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.3</version>
    <configuration>
        <includes>
            <include>**/*Test.java</include>
            <include>**/*Tests.java</include>
            <include>**/Test*.java</include>
        </includes>
        <excludes>
            <exclude>**/*IT.java</exclude>
            <exclude>**/*IntegrationTest.java</exclude>
        </excludes>
        <argLine>-Xmx1024m -XX:+UseG1GC</argLine>
        <parallel>methods</parallel>
        <threadCount>4</threadCount>
        <forkCount>1C</forkCount>
        <reuseForks>true</reuseForks>
        <systemPropertyVariables>
            <spring.profiles.active>test</spring.profiles.active>
        </systemPropertyVariables>
        <environmentVariables>
            <TEST_ENV>true</TEST_ENV>
        </environmentVariables>
    </configuration>
</plugin>
```

### Failsafe Plugin (Integration Tests)

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-failsafe-plugin</artifactId>
    <version>3.2.3</version>
    <configuration>
        <includes>
            <include>**/*IT.java</include>
            <include>**/*IntegrationTest.java</include>
        </includes>
        <skipAfterFailureCount>3</skipAfterFailureCount>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>integration-test</goal>
                <goal>verify</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### JaCoCo Plugin (Code Coverage)

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
    <executions>
        <execution>
            <id>prepare-agent</id>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
        <execution>
            <id>check</id>
            <goals>
                <goal>check</goal>
            </goals>
            <configuration>
                <rules>
                    <rule>
                        <element>BUNDLE</element>
                        <limits>
                            <limit>
                                <counter>LINE</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.80</minimum>
                            </limit>
                            <limit>
                                <counter>BRANCH</counter>
                                <value>COVEREDRATIO</value>
                                <minimum>0.70</minimum>
                            </limit>
                        </limits>
                    </rule>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## Quality Plugins

### Enforcer Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-enforcer-plugin</artifactId>
    <version>3.4.1</version>
    <executions>
        <execution>
            <id>enforce</id>
            <goals>
                <goal>enforce</goal>
            </goals>
            <configuration>
                <rules>
                    <requireMavenVersion>
                        <version>[3.8.0,)</version>
                    </requireMavenVersion>
                    <requireJavaVersion>
                        <version>[17,)</version>
                    </requireJavaVersion>
                    <dependencyConvergence/>
                    <requireUpperBoundDeps/>
                    <banDuplicatePomDependencyVersions/>
                    <bannedDependencies>
                        <excludes>
                            <exclude>commons-logging:commons-logging</exclude>
                            <exclude>log4j:log4j</exclude>
                        </excludes>
                    </bannedDependencies>
                </rules>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### Checkstyle Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-checkstyle-plugin</artifactId>
    <version>3.3.1</version>
    <configuration>
        <configLocation>checkstyle.xml</configLocation>
        <consoleOutput>true</consoleOutput>
        <failsOnError>true</failsOnError>
        <violationSeverity>warning</violationSeverity>
        <includeTestSourceDirectory>true</includeTestSourceDirectory>
    </configuration>
    <executions>
        <execution>
            <id>checkstyle</id>
            <phase>validate</phase>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
    <dependencies>
        <dependency>
            <groupId>com.puppycrawl.tools</groupId>
            <artifactId>checkstyle</artifactId>
            <version>10.12.6</version>
        </dependency>
    </dependencies>
</plugin>
```

### SpotBugs Plugin

```xml
<plugin>
    <groupId>com.github.spotbugs</groupId>
    <artifactId>spotbugs-maven-plugin</artifactId>
    <version>4.8.3.0</version>
    <configuration>
        <effort>Max</effort>
        <threshold>Low</threshold>
        <xmlOutput>true</xmlOutput>
        <excludeFilterFile>spotbugs-exclude.xml</excludeFilterFile>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### PMD Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-pmd-plugin</artifactId>
    <version>3.21.2</version>
    <configuration>
        <rulesets>
            <ruleset>/category/java/bestpractices.xml</ruleset>
            <ruleset>/category/java/errorprone.xml</ruleset>
        </rulesets>
        <failOnViolation>true</failOnViolation>
        <printFailingErrors>true</printFailingErrors>
        <includeTests>true</includeTests>
        <targetJdk>17</targetJdk>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>check</goal>
                <goal>cpd-check</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## Packaging Plugins

### Assembly Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-assembly-plugin</artifactId>
    <version>3.6.0</version>
    <configuration>
        <descriptorRefs>
            <descriptorRef>jar-with-dependencies</descriptorRef>
        </descriptorRefs>
        <archive>
            <manifest>
                <mainClass>com.example.Main</mainClass>
            </manifest>
        </archive>
    </configuration>
    <executions>
        <execution>
            <id>make-assembly</id>
            <phase>package</phase>
            <goals>
                <goal>single</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

### Shade Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-shade-plugin</artifactId>
    <version>3.5.1</version>
    <executions>
        <execution>
            <phase>package</phase>
            <goals>
                <goal>shade</goal>
            </goals>
            <configuration>
                <transformers>
                    <transformer implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                        <mainClass>com.example.Main</mainClass>
                    </transformer>
                    <transformer implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                </transformers>
                <filters>
                    <filter>
                        <artifact>*:*</artifact>
                        <excludes>
                            <exclude>META-INF/*.SF</exclude>
                            <exclude>META-INF/*.DSA</exclude>
                            <exclude>META-INF/*.RSA</exclude>
                        </excludes>
                    </filter>
                </filters>
                <relocations>
                    <relocation>
                        <pattern>com.google</pattern>
                        <shadedPattern>shaded.com.google</shadedPattern>
                    </relocation>
                </relocations>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### WAR Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-war-plugin</artifactId>
    <version>3.4.0</version>
    <configuration>
        <failOnMissingWebXml>false</failOnMissingWebXml>
        <packagingExcludes>WEB-INF/classes/logback-test.xml</packagingExcludes>
        <webResources>
            <resource>
                <directory>src/main/webapp</directory>
                <filtering>true</filtering>
                <includes>
                    <include>**/*.html</include>
                </includes>
            </resource>
        </webResources>
    </configuration>
</plugin>
```

## Spring Boot Plugin

```xml
<plugin>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-maven-plugin</artifactId>
    <version>3.2.0</version>
    <configuration>
        <mainClass>com.example.Application</mainClass>
        <excludes>
            <exclude>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
            </exclude>
        </excludes>
        <layers>
            <enabled>true</enabled>
        </layers>
        <image>
            <name>${project.artifactId}:${project.version}</name>
            <builder>paketobuildpacks/builder:base</builder>
        </image>
    </configuration>
    <executions>
        <execution>
            <goals>
                <goal>repackage</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

## Version Management Plugins

### Versions Plugin

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>versions-maven-plugin</artifactId>
    <version>2.16.2</version>
    <configuration>
        <rulesUri>file:///${project.basedir}/version-rules.xml</rulesUri>
    </configuration>
</plugin>
```

```bash
# Check for updates
mvn versions:display-dependency-updates
mvn versions:display-plugin-updates
mvn versions:display-property-updates

# Update versions
mvn versions:update-properties
mvn versions:use-latest-releases
mvn versions:update-parent
```

### Release Plugin

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-release-plugin</artifactId>
    <version>3.0.1</version>
    <configuration>
        <tagNameFormat>v@{project.version}</tagNameFormat>
        <autoVersionSubmodules>true</autoVersionSubmodules>
        <releaseProfiles>release</releaseProfiles>
    </configuration>
</plugin>
```

## Code Generation Plugins

### Build Helper Plugin

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>build-helper-maven-plugin</artifactId>
    <version>3.5.0</version>
    <executions>
        <execution>
            <id>add-source</id>
            <phase>generate-sources</phase>
            <goals>
                <goal>add-source</goal>
            </goals>
            <configuration>
                <sources>
                    <source>${project.build.directory}/generated-sources</source>
                </sources>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### Exec Plugin

```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>exec-maven-plugin</artifactId>
    <version>3.1.1</version>
    <executions>
        <execution>
            <id>run-script</id>
            <phase>generate-sources</phase>
            <goals>
                <goal>exec</goal>
            </goals>
            <configuration>
                <executable>bash</executable>
                <arguments>
                    <argument>${project.basedir}/scripts/generate.sh</argument>
                </arguments>
            </configuration>
        </execution>
    </executions>
</plugin>
```

## Best Practices

1. **Version Pinning** - Always specify plugin versions
2. **Plugin Management** - Centralize in parent POM
3. **Minimal Configuration** - Use defaults where possible
4. **Execution IDs** - Use meaningful execution IDs
5. **Phase Binding** - Bind to appropriate phases
6. **Skip Properties** - Provide skip properties for flexibility
7. **Documentation** - Comment complex configurations
8. **Inheritance** - Use pluginManagement for multi-module
9. **Updates** - Keep plugins current
10. **Profile Separation** - Separate CI/release plugins into profiles

## Common Pitfalls

1. **Missing Versions** - Relying on default versions
2. **Wrong Phase** - Plugin bound to wrong lifecycle phase
3. **Duplicate Executions** - Same goal running multiple times
4. **Memory Issues** - Insufficient heap for plugins
5. **Ordering** - Plugin execution order conflicts
6. **Inheritance** - Unintended plugin inheritance
7. **Fork Confusion** - Misunderstanding fork behavior
8. **Skip Flags** - Tests accidentally skipped in CI

## When to Use This Skill

- Configuring build compilation settings
- Setting up test frameworks
- Configuring code quality checks
- Creating executable JARs
- Setting up CI/CD builds
- Optimizing build performance
- Generating source code
- Managing releases and versions

[Evidence block]
No Skills: `0`
With Skills: `0`
Delta: `0`
Failure summary: diagnose build break, stage patch diffs, apply fixes, and satisfy build success gate
Competing schema note: No prior round-0 pair evidence available.

[Output contract block]
Return YAML with fields:
revised_task_skill, change_summary{keep/add/remove/sharpen}, rationale

```yaml
revised_task_skill: |
  ...
change_summary:
  keep:
    - ...
  add:
    - ...
  remove:
    - ...
  sharpen:
    - ...
rationale: |
  ...
```

[Outer-loop candidate block]
Source round: outer-loop-round0
Next round: outer-loop-round1
Candidate id: retrieval-heavy-synthesis::round1::differentiating
Candidate mode: differentiating
Pair reason: boundary_case;competitor_check
Next pair plan mode: full_matrix
Use this as a candidate schema rerun, not as an accepted final schema.
