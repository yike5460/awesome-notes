# OpenAPI Design Principles

## Schema

* use verb + noun to construct API call, e.g. do: POST + Inference, don’t: POST + createInference
* avoid multi-layer API URL, use multiple APIs or query string /endpoints/123?type=custom
* conform to HTTP semantics, e.g. GET/PUT/DELETE are idempotent while POST is not
* return JSON or XML instead of plain text
* filter and pagination should be considered, e.g. limit, offset
* considering caching for optimize cost & experience

## Status Code

* return 200 for a successful query
    * List*
    * Get*
* return 201 to indicate resource been created and respond with new resource URL(HATEOAS not supprt yet)
    * Create*
* return 202 (Accepted) in asynchronous API to indicate request was accepted but not completed
    * CreateEndpoint
    * CreateCheckpointByUrl
    * StartInferenceJob
    * StartTrainingJob
* return 204 for a successful delete
    * Delete*
* return 400 for bad request parameters
    * Create*
    * Update*
    * Delete*
    * Start*
* return 401 for unauthorized
* return 403 for forbidden
* return 404 for resource unavailable / not found
    * Get*

```
class HttpStatusCode:
    OK = 200
    Created = 201
    NoContent = 204
    BadRequest = 400
    Forbidden= 403
    NotFound = 404
    InternalServerError = 500

# Mapping status codes to descriptions
http_status_descriptions = {
    HttpStatusCode.OK: "OK",
    HttpStatusCode.Created: "Created",
    HttpStatusCode.NoContent: "No Content",
    HttpStatusCode.BadRequest: "Bad Request",
    HttpStatusCode.Forbidden: "Forbidden",
    HttpStatusCode.NotFound: "Not Found",
    HttpStatusCode.InternalServerError: "Internal Server Error"
}

class StatusCode:
    def __init__(self, code):
        self.code = code
        self.description = http_status_descriptions.get(code, "Unknown Status Code")

    def __str__(self):
        return f"Status Code: {self.code} - {self.description}"
```

## Document

* [HATEOAS](https://restfulapi.net/hateoas/) (Hypertext As The Engineer of Application State) 
* versioning, use URL versioning, query string/header versioning enable existing client continue functioning unchanged while allow new client to explore new feature and resources

## API Version

* x-api-version in Response Header like x-api-key in Request Header
* Auto update by build/release pipeline
