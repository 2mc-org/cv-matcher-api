FROM --platform=linux/amd64 python:3.14

WORKDIR /app
COPY . /app

# Install uv and dependencies
RUN pip install uv
RUN uv sync --frozen

# Generate GraphQL client
RUN make generate-twenty-graphql