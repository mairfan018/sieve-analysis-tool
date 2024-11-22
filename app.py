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
        return None

def create_plot(sieve_data, interpolation_method='linear'):
    """Create particle size distribution plot."""
    plt.style.use('seaborn')
    fig = Figure(figsize=(12, 8))
    ax = fig.add_subplot(111)
    
    # Set up logarithmic scale for x-axis
    ax.set_xscale('log')
    ax.grid(True, which="both", ls="-", alpha=0.2)
    ax.set_xlabel('Particle Size (mm)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Percent Passing (%)', fontsize=12, fontweight='bold')
    ax.set_title('Particle Size Distribution Curve', fontsize=14, fontweight='bold', pad=20)
    
    # Set grid properties
    ax.grid(True, which='major', linestyle='-', alpha=0.5)
    ax.grid(True, which='minor', linestyle='--', alpha=0.3)
    
    # Custom colors with better visibility
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
    
    # Store coefficients for all samples
    all_coefficients = {}
    
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
            x_interp = np.geomspace(min(x), max(x), 200)  # Increased points for smoother curve
            
            # Perform interpolation
            if len(x) >= 4 and interpolation_method == 'cubic':
                y_interp = interpolate.CubicSpline(x, y)(x_interp)
            else:
                y_interp = interpolate.interp1d(x, y, kind=interpolation_method)(x_interp)
            
            # Plot the data
            color = colors[idx % len(colors)]
            ax.plot(x, y, 'o', color=color, markersize=8, label=f'{sample_name} (Data Points)')
            ax.plot(x_interp, y_interp, '-', color=color, linewidth=2, alpha=0.7, label=f'{sample_name} (Interpolated)')
            
            # Calculate coefficients
            coef = calculate_coefficients(x_interp, y_interp)
            if coef:
                all_coefficients[sample_name] = coef
    
    # Add coefficient information to plot
    coef_text = ""
    for idx, (sample_name, coef) in enumerate(all_coefficients.items()):
        if coef:
            coef_text += f"{sample_name}:\n"
            coef_text += f"D10={coef['D10']}, D30={coef['D30']}, D60={coef['D60']}\n"
            coef_text += f"Cu={coef['Cu']}, Cc={coef['Cc']}\n\n"
    
    if coef_text:
        ax.text(1.05, 0.95, coef_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Customize axis
    ax.set_xlim(0.05, 100)
    ax.set_ylim(0, 100)
    
    # Add legend with better placement
    ax.legend(bbox_to_anchor=(1.05, 0.5), loc='center left', fontsize=10)
    
    # Adjust layout to prevent text cutoff
    fig.tight_layout()
    
    # Convert plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    plot_url = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    
    return plot_url, all_coefficients

@app.route('/')
def home():
    return render_template('index.html', sieve_sizes=SIEVE_SIZES)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    sieve_data = data.get('sieve_data', {})
    interpolation_method = data.get('interpolation_method', 'linear')
    
    try:
        plot_url, coefficients = create_plot(sieve_data, interpolation_method)
        return jsonify({
            'success': True,
            'plot': plot_url,
            'coefficients': coefficients
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)
