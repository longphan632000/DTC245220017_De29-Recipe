FROM grafana/promtail@sha256:6cfa64ec432b24a912d640e2edb940eeae2666f61861a66c121d763dd7241381
USER 0
RUN mkdir -p /positions && chown 10001:10001 /positions
USER 10001:10001
