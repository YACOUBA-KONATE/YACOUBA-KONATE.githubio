
---

# Setup

Assuming you have Python and `pip` installed on your computer.

First, clone this repository to your local machine and navigate to the root directory.

Create a virtual environment:

```
python -m venv venv
```

Activate the virtual environment:

```
source venv/bin/activate
```

Install the required libraries:

```
pip install -r requirements.txt
```

Install the `ipykernel` library:

```
pip install ipykernel
```

Add your virtual environment as a Jupyter kernel:

```
python -m ipykernel install --user --name=User-ML
```

Run the Jupyter notebook:

```
jupyter notebook
```

---