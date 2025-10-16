```python
pygame.init()
```

```python
# Initialize pygame
if pg.get_sdl_version()[0] == 2:
    pg.mixer.pre_init(44100, 32, 2, 1024)
pg.init()
if pg.mixer and not pg.mixer.get_init():
    print("Warning, no sound")
    pg.mixer = None
```
