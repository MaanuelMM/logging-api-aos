# Logging API for AOS subject

[Leer en español](./README.es-ES.md)

# Goal

The main goal of this task is to consolidate the concepts related to the specification of a service. For this purpose, the definition of a service will be defined and published using the [OpenAPI 3](http://spec.openapis.org/oas/v3.0.3) standard. Additionally, the behaviour of the service will be simulated (the use of [Stoplight Prism](https://stoplight.io/open-source/prism/), [Postman](https://www.postman.com/), ... is proposed).

# Statement

To achieve this goal, a set of services will be defined and then used to develop a product warehouse management application. First, teams of __a maximum of__ three students will be formed, and each team will have to specify one of the proposed services.

In order to publish the specification, a docker container must be generated to provide the definition of the operations available in the service and describe the connections with other services. The services and the different functionalities that must be implemented must perform the following complete functionalities:

* **Product Management**
  * Adding, deleting and modifying products
  * Adding, deleting and changing categories
  * Product search with free text
  * Listing of products in a category
  * All operations are events to be recorded
* **Order Management**
  * Adding, deleting and modifying orders
  * Order search by type, status, product, organization (customer or supplier) and free text
  * Checking the stock of a product (bought and received - sold and sent or received)
  * All operations are events to be recorded
* **Event Logging** <span style="color:darkmagenta">_**[MICROSERVICE DEVELOPED]**_</span>
  * Event registration
  * Evenet search by origin, level, date range and free text
  * CSV dumping of all events from a given source
  * All operations are events to be recorded
* **Billing**
  * Adding, deleting and modifying organizations
  * Registration and cancellation of invoices
  * Changing an invoice means cancelling it and creating a new one with the changes
  * Invoice search by organization (customer), date range, status and free text
  * All operations are events to be recorded

# Schemas

* [Product](./docs/schemas/Producto.yaml)
* [Category](./docs/schemas/Categoria.yaml)
* [Order](./docs/schemas/Pedido.yaml)
* [Event](./docs/schemas/Evento.yaml)
* [Organization](./docs/schemas/Organizacion.yaml) (proveedores, clientes, ...)
* [Invoice](./docs/schemas/Factura.yaml)

# Notes

* The design of each service will take into account that each service must have its own persistence mechanism
* A single compressed file must be sent in which all the files necessary to deploy the assigned service are attached. A ``README.md`` file must be included, containing the necessary instructions to deploy the developed project
* To carry out this practice, groups of 3 students will be formed. Those students who opt for evaluation by final test only will do the task individually. The service assigned to each student or group of students will be published on the platform.

# The resulting microservice

The microservice developed has been [logging](./docs/schemas/Evento.yaml), which is specificated in [this file](./specification/openapi.yaml).

### Microservice description

#### Schema

The scheme to follow according to the practice statement is the following:

```yaml
Evento:
  title: Evento
  type: objet
  properties:
    evento:
      type: object
      properties:
        idEvento:
          type: integer
          format: int64
          example: 878923748
          minimum: 1
        origen:
          type: string
          example: "PEDIDOS"
        fecha:
          type: string
          format: "date-time"
        mensaje:
          type: string
        nivel:
          type: string
          enum:
            - "info"
            - "warn"
            - "error"
        _links:
          type: object
          description: link relations
          properties:
            parent:
              type: object
              properties: {"href": { "type": "string", "format": "url" }}
            self:
              type: object
              properties: {"href": { "type": "string", "format": "url" }}
  x-examples:
    ejemplo-1:
      idEvento: 89776253
      origen: "PEDIDOS"
      fecha: "2020-03-08T18:30:55.855Z"
      mensaje: "Pedido (compra) 127 realizado. Producto: 12. Cantidad: 2. Organización: 32165478"
      nivel: "info"
      _links:
        parent:
          href: /eventos
        self:
          href: /eventos/89776253
```

#### Endpoints

The microservice has the following endpoints:

* **/events**
    * OPTIONS
    * GET _(application/json | text/csv)_
    * POST _(application/json)_
* **/events/<span style="color:limegreen">{eventId}</span>**
    * OPTIONS
    * GET _(application/json)_

In addition, the ``ETag`` header is used for ``GET`` responses and the ``Allow`` header is used for ``OPTIONS`` responses.

It also has a security mechanism through an ``X-API-Key`` in the header, in order to guarantee the security of access and manipulation of the API data.

Finally, like all ``HTTP`` services, a response code is returned for each request made in order to know if the request was successful or, if not, an error message informing about what happened.

### Microservice interaction

For the interaction with the microservice specification, ``Swagger UI`` will be used, a user interface that allows the display and manipulation of _OpenAPI_ services. In addition, ``Prism`` will be used, a _mock server_ that will allow us to recreate the operation of the service without the need to implement it.

It should be noted that the latter has errors in its different versions, so I have made a [``fork``](https://github.com/MaanuelMM/prism) of version _3.2.9_ applying one of the patches of version _3.3.1_ to handle the ``OPTIONS`` requests with the ``CORS`` header.

#### Running the microservice

##### Requirements

* **Docker Engine** ``18.06.0`` or higher (make sure the service is running).

##### Starting the microservice

Open a terminal (with administrator privileges if the Docker pipeline does not have such permissions assigned) and go to the root directory of this project. Then run the following command to up the microservices:

```console
foo@bar:~$ docker-compose -f docker-compose.yaml up
```

If this fails, make sure you don't have any Docker containers with the same name running, and don't use the same port (if necessary, change the port in the ``docker-compose.yaml`` file).

##### Using the microservice

Open the browser and type ``localhost`` (if you have changed the port, type the port as follows: ``localhost:<port>``).

Once there, you can test, as indicated by the Swagger UI user interface, each of the available requests along with the required parameters. You can also view the console-generated logs to see how the requests are made and how the _mock server_ resolves them.

##### Stopping the microservice

Once the manipulation of the microservice has been completed, you can end the execution of the microservice with ``Ctrl + C``.

You should also remove the created containers to avoid future problems, as the _Prism_ server requires their removal if you want to re-launch the container (otherwise it will not work). To do this you must execute the following command:

```console
foo@bar:~$ docker-compose -f docker-compose.yaml rm
```

These steps should also be performed if by any chance the service fails while running and needs to be restarted, stopping and removing the containers created first and launching them again for proper execution.