FROM ollama/ollama

RUN mkdir -p /root/.ollama/models
COPY models /root/.ollama/models/

ENV OLLAMA_HOST=0.0.0.0
EXPOSE 11434

ENTRYPOINT ["ollama"]
CMD ["serve"]