# init
```python
try:
    import OpenGL.GL as GL
    import OpenGL.GLU as GLU
except ImportError:
    print("pyopengl missing. The GLCUBE example requires: pyopengl numpy")
    raise SystemExit
```