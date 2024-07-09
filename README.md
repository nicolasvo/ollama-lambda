# goal

deploy an ollama server using aws lambda

## steps
1. build docker image in `lambda/`
2. terraform ecr (elastic container registry) in `terraform/ecr/`
3. push docker image
4. terraform lambda