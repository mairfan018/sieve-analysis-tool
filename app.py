from flask import Flask, render_template, request, jsonify
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.figure import Figure
import os

app = Flask(__name__)

# Standard sieve sizes (IS)
SIEVE_SIZES = [0.075, 0.15, 0.3, 0.6, 1.18, 2.36, 4.75, 10.0, 20.0, 40.0, 53.0]

def calculate_coefficients(x_interp, y_interp):
    """Calculate D10, D30, D60, Cu, and Cc values."""
    try:
        # Create interpolation function for particle size at given percent passing
        interp_func = interpolate.interp1d(y_interp, x_interp, bounds_error=False, fill_value="extrapolate")
        
        # Calculate D values
        D10 = float(interp_func(10))
        D30 = float(interp_func(30))
        D60 = float(interp_func(60))
        
        # Calculate coefficients
        Cu = D60 / D10
        Cc = (D30 ** 2) / (D10 * D60)
        
        return {
            'D10': round(D10, 3),
            'D30': round(D30, 3),
            'D60': round(D60, 3),
            'Cu': round(Cu, 3),
            'Cc': round(Cc, 3)
        }
    except:
        return {
            'D10': None,
            'D30': None,
            'D60': None,
            'Cu': None,
            'Cc': None
        }

def create_plot(sieve_data, interpolation_method='linear'):
    """Create particle size distribution plot."""
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    # Set up logarithmic scale for x-axis
    ax.set_xscale('log')
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.set_xlabel('Particle Size (mm)')
    ax.set_ylabel('Percent Passing (%)')
    ax.set_title('Particle Size Distribution Curve')
    
    colors = ['b', 'r', 'g', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']
    
    for idx, (sample_name, data) in enumerate(sieve_data.items()):
        x_values = []
        y_values = []
        
        # Organize data
        for size, passing in zip(SIEVE_SIZES, data):
            if passing is not None:
                x_values.append(size)
                y_values.append(passing)
        
        if x_values and y_values:
            # Convert to numpy arrays
            x = np.array(x_values)
            y = np.array(y_values)
            
            # Create interpolation points
            x_interp = np.geomspace(min(x), max(x), 100)
            
            # Perform interpolation
            if len(x) >= 4 and interpolation_method == 'cubic':
                y_interp = interpolate.CubicSpline(x, y)(x_interp)
            else:
                y_interp = interpolate.interp1d(x, y, kind=interpolation_method)(x_interp)
            
            # Plot the data
            color = colors[idx % len(colors)]
            ax.plot(x, y, color + 'o', label=f'{sample_name} (Data Points)')
            ax.plot(x_interp, y_interp, color + '-', label=f'{sample_name} (Interpolated)')
            
            # Calculate and display coefficients
            coef = calculate_coefficients(x_interp, y_interp)
            if all(v is not None for v in coef.values()):
                ax.text(0.02, 0.98 - idx*0.1, 
                       f'{sample_name}: Cu={coef["Cu"]}, Cc={coef["Cc"]}',
                       transform=ax.transAxes, fontsize=8)
    
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    fig.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return plot_url

@app.route('/')
def home():
    return render_template('index.html', sieve_sizes=SIEVE_SIZES)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sieve_data = data.get('sieve_data', {})
    interpolation_method = data.get('interpolation_method', 'linear')
    
    try:
        plot_url = create_plot(sieve_data, interpolation_method)
        return jsonify({
            'success': True,
            'plot': plot_url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
