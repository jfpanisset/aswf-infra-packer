FROM jenkins/jenkins:lts
USER jenkins
COPY executors.groovy /usr/share/jenkins/ref/init.groovy.d/executors.groovy
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
