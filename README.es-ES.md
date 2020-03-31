# API de Registro de Eventos (logging) para la asignatura de AOS

[Return to English version](./README.md)

## Objetivo

El principal objetivo de esta tarea consiste en consolidar los conceptos relacionados con la especificación de un servicio. Para ello se definirá y publicará la definición de un servicio empleando el estándar [OpenAPI 3](http://spec.openapis.org/oas/v3.0.3). Adicionalmente se simulará el comportamiento del servicio (se propone el empleo de [Stoplight Prism](https://stoplight.io/open-source/prism/), [Postman](https://www.postman.com/), ...)

## Enunciado

Para conseguir este objetivo se van a definir un conjunto de servicios que, posteriormente, se emplearán para desarrollar una aplicación de gestión de un almacén de productos. En primer lugar se formarán equipos de __como máximo__ tres alumnos, y cada equipo deberá realizar la especificación de uno de los servicios propuestos.

Para publicar la especificación se deberá generar un contenedor docker que ofrezca la definición de las operaciones disponibles en el servicio y describa las conexiones con otros servicios. Los servicios y las diferentes funcionalidades que se deberán implementar deberán realizar las siguientes funcionalidades completas:

* **Gestión de Productos**
    * Alta, baja y modificación de productos
    * Alta, baja y modificación de categorías
    * Búsqueda de productos con texto libre
    * Listado de productos de una categoría
    * Todas las operaciones son eventos a registrar
* **Gestión de Pedidos**
    * Alta, baja y modificación de pedidos
    * Búsqueda de pedidos por tipo, estado, producto, organización (cliente o proveedor) y texto libre
    * Consulta de stock de un producto (comprados y recibidos - vendidos y enviados o recibidos)
    * Todas las operaciones son eventos a registrar
* **Registro de Eventos (logging)** <span style="color:darkmagenta">_**[MICROSERVICIO REALIZADO]**_</span>
    * Alta de eventos
    * Búsqueda de eventos por origen, nivel, rango de fechas y texto libre
    * Volcado en CSV de todos los eventos de un determinado origen
    * Todas las operaciones son eventos a registrar
* **Facturación**
    * Alta, baja y modificación de organizaciones
    * Alta y cancelación de facturas
    * La modificación de una factura implica baja de la misma y creación de una nueva con los cambios
    * Búsqueda de facturas por organización (cliente), rango de fecha, estado y texto libre
    * Todas las operaciones son eventos a registrar

## Esquemas

* [Producto](./docs/schemas/Producto.yaml)
* [Categoría](./docs/schemas/Categoria.yaml)
* [Pedido](./docs/schemas/Pedido.yaml)
* [Evento](./docs/schemas/Evento.yaml)
* [Organización](./docs/schemas/Organizacion.yaml) (proveedores, clientes, ...)
* [Factura](./docs/schemas/Factura.yaml)

## Notas

* En el diseño de cada servicio se tendrá en cuenta que cada uno de los servicios deberá contar con su propio mecanismo de persistencia
* Se deberá enviar un único fichero comprimido en el que se adjuntarán todos los ficheros necesarios para desplegar el servicio asignado. Obligatoriamente se incluirá un Fichero ``README.md`` que contendrá las instrucciones necesarias para desplegar el proyecto desarrollado
* Para realizar esta práctica se formarán grupos de 3 alumnos. Aquellos alumnos que opten por evaluación solo por prueba final realizarán el ejercicio de manera individual. En la plataforma se publicará el servicio asignado a cada alumno o grupo de alumnos.

## Microservicio resultante

El microservicio realizado ha sido el de [logging](./docs/schemas/Evento.yaml), el cual se encuentra especificado en [este fichero](./specification/openapi.yaml).

### Descripción del microservicio

#### Esquema

El esquema a seguir según el enunciado de la práctica es el siguiente:

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

El microservicio cuenta con los siguientes endpoints:

* **/events**
    * OPTIONS
    * GET _(application/json | text/csv)_<span style="color:orangered"> _[?query=search]_</span>
    * POST _(application/json)_
* **/events/<span style="color:limegreen">{eventId}</span>**
    * OPTIONS
    * GET _(application/json)_

Además, se hace uso de la cabecera ``Etag`` para las respuestas de los ``GET`` y la cabecera ``Allow`` para las respuestas de los ``OPTIONS``.

También cuenta con un mecanismo de seguridad mediante una ``X-API-Key`` en la cabecera, con el fin de garantizar la seguridad de acceso y manipulación de los datos de la API.

Por último, al igual que todo servicio ``HTTP``, se devuelve un código de respuesta para cada petición realizada con el fin de saber si la petición se realizó correctamente o, en su defecto, un mensaje de error informando de lo sucedido.

### Interacción con el microservicio

Para la interacción con la especificación del microservicio, se hará uso de ``Swagger UI``, una interfaz de usuario que permite la visualización y manipulación de servicios _OpenAPI_. Además, se empleará ``Prism``, un _mock server_ que nos permitirá recrear el funcionamiento del servicio sin necesidad de implementar este.

Cabe destacar que este último tiene errores en sus distintas versiones, por lo que he realizado un [``fork``](https://github.com/MaanuelMM/prism) de la versión _3.2.9_ aplicando uno de los parches de la versión _3.3.1_ para manejar las peticiones ``OPTIONS`` con la cabecera ``CORS``.

#### Ejecución del microservicio

##### Requisitos

* **Docker Engine** ``18.06.0`` o superior (asegúrate de que el servicio se encuentre arrancado).

##### Arrancando el microservicio

Abre una terminal (con privilegios administrador si el pipeline de Docker no tiene dichos permisos asignados) y sitúate en el directorio raíz de este proyecto. A continuación, ejecuta el siguiente comando para levantar los microservicios:

```console
foo@bar:~$ docker-compose -f docker-compose.yaml up
```

Si este falla, asegúrate de no tener arrancado ningún contenedor Docker que tenga el mismo nombre, así como de no usar el mismo puerto (si fuese necesario, cambie el puerto en el fichero ``docker-compose.yaml``).

##### Usando el microservicio

Abre el navegador y escribe ``localhost`` (si hubiese cambiado de puerto, escriba el puerto de la siguiente forma: ``localhost:<port>``).

Una vez ahí, podrá probar, tal y como le indica la interfaz de usuario de Swagger UI, cada una de las peticiones disponibles junto con los parámetros requeridos. También podrá ver los logs generados por consola para ver cómo se realizan las peticiones y cómo lo resuelve el _mock server_.

##### Finalizando el microservicio

Una vez finalice la manipulación del microservicio, podrá finalizar la ejecución del mismo con ``Ctrl + C``.

También deberá eliminar los contenedores creados para evitar futuros problemas, pues el servidor _Prism_ requiere de su eliminación si se desea volver a lanzar el contenedor (de lo contrario no funcionará). Para ello deberá ejecutar el siguiente comando:

```console
foo@bar:~$ docker-compose -f docker-compose.yaml rm
```

Estos pasos también deberán de ser realizados si por algún casual el servicio falla mientras se ejecuta y necesita ser reiniciado, parando y eliminando primero los contenedores creados y volviéndolos a lanzar de nuevo para su correcta ejecucción.