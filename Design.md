# 1.Choosing technologies
## 1.1 What ChatGPT has to say about it : 

> 
>Database Technology
>
>1. PostgreSQL
>
>    Pros:
>        Mature, robust, and widely supported relational database.
>        Good support for JSON data, which can be useful for storing app parameters.
>        Can handle complex queries and large datasets.
>        Extensions like PostGIS for spatial data.
>    Cons:
>        Requires more setup and maintenance compared to some NoSQL databases.
>        Might not be as performant as specialized databases for specific workloads.
>
>2. MongoDB
>
>    Pros:
>        Schema-less, which allows for flexible and rapid development.
>        Good for storing JSON-like documents.
>        Built-in support for horizontal scaling and high availability.
>        GridFS for efficient image storage.
>    Cons:
>        Less mature querying capabilities compared to SQL databases.
>        Potentially higher memory usage.
>        Requires careful schema design to avoid performance issues at scale.
>
>3. Amazon S3 (for image storage) with DynamoDB (for metadata)
>
>    Pros:
>        S3 is highly scalable and durable for storing images.
>        DynamoDB is a fully managed NoSQL database, which can handle high throughput.
>        Integration with other AWS services for analytics and machine learning.
>    Cons:
>        Vendor lock-in to AWS.
>        Requires managing two different services.
>        Can be more expensive than self-hosted solutions.
>
>4. SQLite
>
>    Pros:
>        Simple and easy to set up, ideal for prototyping and small applications.
>        No server required; the database is just a file on disk.
>    Cons:
>        Not suitable for high-concurrency or large-scale applications.
>        Limited querying capabilities compared to full-fledged SQL databases.
>
>Front-End Technologies
>
>1. Flask with Jinja2 Templates
>
>    Pros:
>        Lightweight and easy to get started with.
>        Highly customizable and flexible.
        Excellent documentation and large community support.
    Cons:
        Requires more boilerplate code for features like authentication.
        Not as feature-rich out-of-the-box compared to larger frameworks.
>
>2. Django
>
>    Pros:
>        Comprehensive framework with built-in authentication, ORM, and admin interface.
>        Encourages best practices and scalable architecture.
>        Large community and extensive documentation.
>    Cons:
>        Can be overkill for smaller projects.
>        Steeper learning curve compared to Flask.
>
>3. FastAPI with a front-end framework (e.g., React, Vue.js)
>
>    Pros:
>        Modern, high-performance, and asynchronous web framework.
>        Automatic generation of OpenAPI documentation.
>        Can handle real-time updates with WebSockets.
>    Cons:
>        Requires learning and managing both backend (FastAPI) and frontend (React/Vue).
>        Less mature compared to Flask and Django.
>
>Machine Learning Frameworks
>
>1. TensorFlow/Keras
>
>    Pros:
>        Widely used and supported by a large community.
>        Good for both research and production.
>        Strong support for deploying models (e.g., TensorFlow Serving).
>    Cons:
>        Can be complex and verbose for simple tasks.
>        Steeper learning curve compared to some other frameworks.
>
>2. PyTorch
>
>    Pros:
>        Flexible and user-friendly, popular in the research community.
>        Dynamic computation graph makes debugging easier.
>        Strong support for deploying models (e.g., TorchServe).
>    Cons:
>        Historically considered less production-ready than TensorFlow (though this has changed).
>        Smaller ecosystem compared to TensorFlow.
>
>3. OpenCV (for image processing)
>
>    Pros:
>        Comprehensive library for image processing tasks.
>        Integrates well with both TensorFlow and PyTorch.
>        Extensive documentation and community support.
>    Cons:
>        Focused more on image processing than machine learning.
>        May require additional setup for complex machine learning tasks.
>
>API Frameworks
>
>1. FastAPI
>
>    Pros:
>        Fast, asynchronous, and modern API framework.
>        Automatic generation of interactive API documentation.
>        High performance and easy integration with Python-based machine learning models.
>    Cons:
>        Relatively new, so the ecosystem is not as mature as some other frameworks.
>        Asynchronous programming might have a learning curve.
>
>2. Flask-RESTful
>
>    Pros:
>        Simple and lightweight.
>        Good for building small to medium-sized APIs.
>        Easy to integrate with existing Flask applications.
>    Cons:
>        Not as feature-rich as FastAPI for modern API requirements.
>        Requires additional extensions for things like validation and authentication.
>
>3. Django REST Framework (DRF)
>
>    Pros:
>        Fully featured and highly customizable.
>        Strong integration with Django models and authentication.
>        Excellent documentation and community support.
>    Cons:
>        Can be overkill if you're not already using Django.
>        Higher initial setup complexity compared to Flask-RESTful or FastAPI.
>
>Summary
>
>    Database: PostgreSQL or MongoDB for general use. Use Amazon S3 with DynamoDB if you prefer a managed solution with separate image storage.
>    Front-End: Flask or Django for simplicity and rapid development. Consider FastAPI with a frontend framework like React for a more modern, scalable solution.
>    Machine Learning: TensorFlow/Keras or PyTorch for model training and deployment, with OpenCV for image processing tasks.
>    API: FastAPI for a modern, high-performance API. Flask-RESTful for simplicity, or Django REST Framework for a comprehensive solution integrated with Django.
>
>These technologies should provide a robust foundation for building your computer vision application tailored for sports shooters.


## 1.2 My take

### Database

It looks to me that storing images directly in a DB is highly inefficient. 
As a certain SO post encounter during my research justly put it:
> Your File system is a type of databae that is optimized to store files.
A SQLite or MariaDB instance will be plenty to cover application data and parameters.

![database_schema](Database/static/schema.png)

### File server

The obvious choice for this project would be Azure blob Storage as Simplon Microsoft Credits would greatly simplify access. Cost optimization should still be considred.

### ML model

__TBD__

### API

I'm more lenient towards FastAPI these days for several reasons : 
+ Easy to set up 
+ Automatic documentation
+ Swagger requests test
+ local test using uvicorn
+ for local test i can plug it in streamlit, and consume it through the real front end for production 

### front-end

For a mobile app, several options : 
- Using Xamarin for coding the front in C#, but could be a challenge to set up a Visual Studio instance on my linux machine without the hassle of setting up a VM
- Flutter, but I them need to learn Dart
- PyQt allowing me to stay in the python ecosystem.

It appears to me that choosing the PyQt route is the more desirable as it will allow me to hone my python skill and could be a cool challenge. Plus, I tried the QtTile Windows Manager on my machine a saw that it allows to produce something very cool looking. 


