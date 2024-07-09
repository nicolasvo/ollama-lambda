# aws lambda with response streaming

## how
[aws-lambda-web-adapter](https://github.com/awslabs/aws-lambda-web-adapter) is what enables turning any container into a lambda, as long as it can be requested via HTTP.

this project is inspired by this implementation of fastapi response streaming: https://github.com/awslabs/aws-lambda-web-adapter/tree/main/examples/fastapi-response-streaming

finally, the terraform of aws_lambda_function_url defines: `invoke_mode = "RESPONSE_STREAM"`

## two lambdas
here i propose two approaches:
1. lambda with ollama server only
2. lambda with python fastapi which redirects the streaming output of ollama server

the first approach is simple and the second one let's you do more things:
- process generated output
- modify api routes and request parameters
- etc.

## setup
- in the Dockerfile, replace `ARG MODEL=` with the ollama model you want to serve
- (optional) instead of pulling the model during image build, if you have pulled the model locally, you can copy it to the imaage: `COPY models /app/ollama_data/models/`

## test request (locally)
### 1. lambda ollama only
- build image: `docker build -f Dockerfile.ollama -t lambda:ollama .`
- run container: `docker run -it --rm -p 11434:11434 lambda:ollama`
- curl request (set stream to `true` or `false`):
```
curl http://localhost:11434/api/generate -d '{
  "model": "tinyllama:1.1b",
  "prompt": "why is the sky blue",
  "stream": true
}'
```

### 2. lambda fastapi ollama
- build image: `docker build -f Dockerfile.fastapi -t lambda:fastapi .`
- run container: `docker run -it --rm -p 8080:8080 lambda:ollama`
- curl request (set stream to `true` or `false`, defaults to `false`):
```
curl http://localhost:8080/generate -d '{
  "prompt": "why is the sky blue",
  "stream": true
}'
```
## test request (on aws lambda)
- same curl request but replace localhost:PORT with aws lambda function url (no need to specify port because url already redirects to it)