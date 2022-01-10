# SearchEngine


Welcome to our search engine over the whole wikipedia corpus (over 6 million documents)

## How To Start

open new python file and send requests to the engine

```python
import request
response = request.get(url="http://34.72.166.196/search",params={"query":"hello world"})
```

## Run Engine Locally

### clone repository
```bash
git clone https://github.com/ItayDarBeMi/SearchEngine.git
```
### start server
```bash
python Engine/search_frontend.py
```
