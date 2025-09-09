from wsgiref.simple_server import make_server
import time, json, random
def app(env,start):
    if env.get('PATH_INFO')!='/dev/sse':
        start('404 Not Found',[('Content-Type','text/plain')]); return [b'Nope']
    start('200 OK',[('Content-Type','text/event-stream'),('Cache-Control','no-cache'),('Connection','keep-alive'),('Access-Control-Allow-Origin','*')])
    def gen():
        raised, goal = 0, 10000
        while True:
            raised = min(goal, raised + random.randint(40,120))
            yield f"data: {json.dumps({'raised':raised,'goal':goal})}\n\n"; time.sleep(2)
    return gen()
print("SSE @ http://localhost:5055/dev/sse")
make_server('', 5055, app).serve_forever()
