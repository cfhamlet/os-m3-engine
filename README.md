# os-3m-engine

[![Build Status](https://www.travis-ci.org/cfhamlet/os-3m-engine.svg?branch=master)](https://www.travis-ci.org/cfhamlet/os-3m-engine)
[![codecov](https://codecov.io/gh/cfhamlet/os-3m-engine/branch/master/graph/badge.svg)](https://codecov.io/gh/cfhamlet/os-3m-engine)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/os-3m-engine.svg)](https://pypi.python.org/pypi/os-3m-engine)
[![PyPI](https://img.shields.io/pypi/v/os-3m-engine.svg)](https://pypi.python.org/pypi/os-3m-engine)

Multi-thread engine for 3(or 2) stages job.



Although multi-thread of python is buggy and slow, it is still necessary to write multi-thread program. Typically, producer-consumer is the most common model(so called 2-stage job), further more a transporter is needed between them(3-stage job). This library is used to simplify creating 3(or 2) stages program. 



The 3 stages are:

* Frontend: think as producer, usually used to create or receive data.
* Transport: receive data from frontend stage, transform and send the transformed data to backend.
* Backend: think as consumer, process the data received from transport.



Something else need to know:

* Each of the stage can be multi-thread.
* Frontend is required, transport or backend can be omitted.




# Install

`pip install os-3m-engine`

# API

* Create a default engine, a typical 3-stage job:

    frontend: ``os_3m_engine.ootb.StdinFrontend``, read from stdin, send to transport stage
    transport: ``os_3m_engine.ootb.LogTransport``, log data received from fronted, send to backend stage
    backend: ``os_3m_engine.ootb.LogBackend``, log data received from transport

    ```
    from os_3m_engine.launcher import create
    
    engine = create()
    ```

* Create engine with custom defined stage:

    ```
    from os_3m_engine.launcher import create
    
    engine = create(transport_cls='transport_class_path_or_class')
    ```

* Create engine with custom engine config:

    ```
    from os_3m_engine.launcher import create
    
    config = WhateverOjbectYouWant
    config.thread_num = 10
    engine = create(transport_cls='your_transport_cls', engine_transport_config=config) 
    ```

* Start the engine:

    ``start`` will block the current thread until all of the stage threads stopped
    
    ```
    engine.start()
    ```

* The regular practice of stopping the engine

    ```
    from signal
    from os_3m_engine.launcher import create
    
    engine = create()
    
    def stop(signum, frame):
        engine.stop()
    
    signal.signal(signal.SIGINT, stop)
    
    engine.start()
    ```
    
* Custom frontend class:

    1. inherit from ``os_3m_engine.core.frontend.Frontend``
    2. define ``produce`` method as generator

    ```
    from os_3m_engine.core.frontend import Frontend
    
    class CustomFrontend(Frontend):
        def produce(self):
            yield 'Hello world!'
    ```
    
* Custom transport class:

    1. inherit from ``os_3m_engine.core.transport.Transport``
    2. define ``transport`` method, the only parameter is the data received, the return value will be sent to backend

    ```
    from os_3m_engine.core.transport import Transport
    
    class CustomTransport(Transport):
        def transport(self, data):
            return data
    ```

* Custom backend class:

    1. inherit from ``os_3m_engine.core.backend.Backend``
    2. define ``process`` method, the only parameter is the data received, no need return

    ```
    from os_3m_engine.core.backend import Backend
    
    class CustomBackend(Backend):
        def process(self, data):
            print(data)
    ```

* Passing parameters

    * create engine with custom config object
    * use ``self.config`` to get the config in stage class

    ```
    from os_3m_engine.launcher import create
    
    config = WhateverOjbectYouWant
    engine = create(app_config=config)
    ```


* Custom ``setup``, ``cleanup`` behavior
  
    each stage class can define ``setup``, ``cleanup`` methods, these will be called at each thread start/stop
    
    
    ```
    from os_3m_engine.core.backend import Backend
    
    class CustomBackend(Backend):
    
        def setup(self):
            print('Setup')
            
        def cleanup(self):
            print('Cleanup')
        
        def process(self, data):
            print(data)
    ```



# Unit Tests

`$ tox`

# License

MIT licensed.
