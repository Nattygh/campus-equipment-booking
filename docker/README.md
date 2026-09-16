# Running Jenkins locally (Docker)

1. From `docker/`: `docker compose up -d`
2. Jenkins: http://localhost:8080. Get the initial admin password with
   `docker exec equipment-booking-jenkins cat /var/jenkins_home/secrets/initialAdminPassword`
3. Install the suggested plugins, then create a Pipeline job pointing at
   this repository's `Jenkinsfile`.
4. A standalone Selenium Chrome container is on `localhost:4444` for the
   E2E stage.
5. Ensure Python 3.12 is available on the Jenkins agent.

**Known limitation:** Jenkins was not executed as part of building this
project (Docker-in-Docker isn't available in the development sandbox used
to build it). Run it once locally per these steps before submission and
capture the console output for the Test Summary Report.
