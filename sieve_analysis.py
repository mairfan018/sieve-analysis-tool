import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate

# Sieve sizes (mm) - IS Standard
sieve_sizes = np.array([0.075, 0.15, 0.3, 0.6, 1.18, 2.36, 4.75, 10.0, 20.0, 40.0, 53.0])

# Percentage passing data
fa_passing = np.array([np.nan, np.nan, np.nan, 100, 98.8, 76.2, np.nan, 43.3, 22, np.nan, 10, 1.8, np.nan])
soil_passing = np.array([np.nan, np.nan, np.nan, 100, 91.5, np.nan, 69.5, np.nan, np.nan, 31.8, np.nan, np.nan, 20.7])
ca_passing = np.array([100, 96.38, 59, 40.1, 18.7, 12.2, np.nan, 5.05, 2.75, np.nan, 1.65, 1.1, 0.5])
regraded_soil = np.array([np.nan, np.nan, np.nan, 100, 100, np.nan, 75.96, np.nan, np.nan, 34.75, np.nan, np.nan, 22.62])

def handle_null_values(x, y, method='interpolate', interp_method='cubic', allow_extrapolation=False):
    """
    Handle null values in the data.
    
    Args:
        x: Array of x values (sieve sizes)
        y: Array of y values (passing percentages) with possible None values
        method: How to handle null values ('interpolate', 'ignore', 'zero')
        interp_method: Interpolation method ('linear', 'cubic', 'nearest')
        allow_extrapolation: Whether to allow extrapolation beyond data points
    
    Returns:
        Tuple of (x_clean, y_clean) with handled null values
    """
    # Convert to numpy arrays
    x = np.array(x)
    y = np.array(y, dtype=float)
    
    # Find indices of non-null values
    valid_mask = ~np.isnan(y)
    
    if method == 'zero':
        # Replace null values with zeros
        y[~valid_mask] = 0
        return x, y
    
    elif method == 'ignore':
        # Remove null values
        return x[valid_mask], y[valid_mask]
    
    else:  # method == 'interpolate'
        if sum(valid_mask) < 2:
            raise ValueError("Need at least 2 non-null points for interpolation")
        
        # Create interpolation function
        bounds_error = not allow_extrapolation
        f = interpolate.interp1d(
            x[valid_mask],
            y[valid_mask],
            kind=interp_method,
            bounds_error=bounds_error,
            fill_value='extrapolate' if allow_extrapolation else np.nan
        )
        
        # Interpolate null values
        y[~valid_mask] = f(x[~valid_mask])
        return x, y

def calculate_dx(x, y, percent):
    """Calculate Dx value (particle size at x% passing)."""
    if len(x) < 2:
        return np.nan
    
    f = interpolate.interp1d(y, x, bounds_error=False, fill_value=np.nan)
    return float(f(percent))

def generate_plot(samples_data, use_color=True, interp_method='cubic', 
                 null_method='interpolate', allow_extrapolation=False):
    """
    Generate sieve analysis plot from sample data.
    
    Args:
        samples_data: List of dictionaries containing sample data
            Each dictionary should have:
            - name: Sample name
            - sizes: List of sieve sizes in mm
            - values: List of passing percentages (can contain None)
            - null_indices: List of indices where values are null
        use_color: Boolean indicating whether to use color or grayscale
        interp_method: Method for interpolation ('linear', 'cubic', 'nearest')
        null_method: How to handle null values ('interpolate', 'ignore', 'zero')
        allow_extrapolation: Whether to allow extrapolation beyond data points
    """
    # Create figure and subplots with A4 landscape size (11.69 × 8.27 inches)
    fig = plt.figure(figsize=(11.69, 8.27))
    gs = plt.GridSpec(2, 1, height_ratios=[1.8, 1], figure=fig)
    ax_plot = fig.add_subplot(gs[0])
    ax_table = fig.add_subplot(gs[1])

    # Set plot background color to white for better printing
    ax_plot.set_facecolor('white')
    fig.patch.set_facecolor('white')

    # Format axes
    ax_plot.set_xscale('log')
    ax_plot.xaxis.set_major_formatter(plt.FormatStrFormatter('%.3f'))
    ax_plot.set_ylim(0, 100)
    ax_plot.set_yticks(np.arange(0, 101, 10))

    # Create color scheme
    if use_color:
        colors = ['#FF4B4B', '#4B4BFF', '#4BFF4B', '#FF4BFF']  # Red, Blue, Green, Magenta
    else:
        colors = ['#000000', '#404040', '#808080', '#B0B0B0']  # Black to Light Gray

    # Process and plot each sample
    table_data = []
    table_colors = []
    
    for idx, sample in enumerate(samples_data):
        # Get sample data
        name = sample['name']
        x = np.array(sample['sizes'])
        y = np.array([np.nan if v is None else v for v in sample['values']])
        color = colors[idx % len(colors)]
        
        # Handle null values
        x_clean, y_clean = handle_null_values(
            x, y,
            method=null_method,
            interp_method=interp_method,
            allow_extrapolation=allow_extrapolation
        )
        
        # Create interpolation function for smooth curve
        f = interpolate.interp1d(
            np.log10(x_clean),
            y_clean,
            kind=interp_method,
            bounds_error=False,
            fill_value='extrapolate' if allow_extrapolation else np.nan
        )
        
        # Create dense points for smooth curve
        x_dense = np.geomspace(min(x_clean), max(x_clean), 2000)
        y_dense = f(np.log10(x_dense))
        
        # Plot the curve
        ax_plot.plot(x_dense, y_dense, color=color, label=name)
        
        # Plot original points (non-null values only)
        valid_mask = ~np.isnan(y)
        ax_plot.plot(x[valid_mask], y[valid_mask], 'o', color=color, markersize=6)
        
        # Plot interpolated points (null values) with different marker
        if null_method != 'ignore':
            null_mask = np.isnan(y)
            ax_plot.plot(x[null_mask], y_clean[null_mask], 's', color=color, 
                        markersize=6, mfc='none', label=f"{name} (interpolated)")
        
        # Calculate D values and coefficients
        d10 = calculate_dx(x_dense, y_dense, 10)
        d30 = calculate_dx(x_dense, y_dense, 30)
        d60 = calculate_dx(x_dense, y_dense, 60)
        
        if np.isnan(d10) or np.isnan(d30) or np.isnan(d60):
            cu = np.nan
            cc = np.nan
            classification = "Insufficient\ndata"
        else:
            cu = d60 / d10
            cc = (d30 ** 2) / (d10 * d60)
            
            # Determine classification
            if cu > 4 and 1 <= cc <= 3:
                classification = "Well-graded"
            else:
                classification = "Poorly-graded\n"
                reasons = []
                if cu <= 4:
                    reasons.append("Cu ≤ 4")
                if cc < 1 or cc > 3:
                    reasons.append("Cc outside 1-3")
                if reasons:
                    classification += f"({', '.join(reasons)})"
        
        table_data.append([
            f'{d10:.3f}' if not np.isnan(d10) else 'N/A',
            f'{d30:.3f}' if not np.isnan(d30) else 'N/A',
            f'{d60:.3f}' if not np.isnan(d60) else 'N/A',
            f'{cu:.2f}' if not np.isnan(cu) else 'N/A',
            f'{cc:.2f}' if not np.isnan(cc) else 'N/A',
            classification
        ])
        table_colors.append(color)

    # Add grid and labels
    ax_plot.grid(True, which='both', linestyle='-', alpha=0.2)
    ax_plot.set_xlabel('Particle Size (mm)')
    ax_plot.set_ylabel('Percent Passing (%)')
    ax_plot.set_title('Particle Size Distribution')

    # Add legend
    legend = ax_plot.legend(loc='upper right', bbox_to_anchor=(1, 1), fontsize=10)
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(0.8)

    # Create table
    columns = ['D10\n(mm)', 'D30\n(mm)', 'D60\n(mm)', 
              'Cu\n(D60/D10)', 'Cc\n(D30²/D10×D60)', 'Classification']
    rows = [sample['name'] for sample in samples_data]

    # Hide table subplot axis
    ax_table.axis('off')

    # Create and style the table
    table = ax_table.table(cellText=table_data,
                          rowLabels=rows,
                          colLabels=columns,
                          cellLoc='center',
                          loc='center',
                          bbox=[0.05, 0.1, 0.95, 0.85])

    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.5, 1.8)

    # Style cells
    for i in range(len(rows) + 1):
        for j in range(-1, len(columns)):
            if (i, j) in table._cells:
                cell = table._cells[(i, j)]
                cell._loc = 'center'
                
                if i == 0:  # Header row
                    cell.set_text_props(weight='bold', linespacing=1.2)
                    cell.set_facecolor('#d0d0d0')
                    cell._height *= 1.2
                
                if j == 5:  # Classification column
                    cell.set_text_props(linespacing=1.2, wrap=True)

    # Add colors and styling to table cells
    for idx, color in enumerate(table_colors):
        if use_color:
            table[(idx+1, -1)].set_text_props(color=color)
        
        for j in range(len(columns)):
            cell = table[(idx+1, j)]
            cell.set_facecolor('white')
            
            if table_data[idx][j] == 'N/A':
                cell.set_facecolor('#f0f0f0')
            elif j == 3 and table_data[idx][j] != 'N/A' and float(table_data[idx][j]) <= 4:  # Cu column
                cell.set_facecolor('#f0f0f0')
            elif j == 4 and table_data[idx][j] != 'N/A' and (float(table_data[idx][j]) < 1 or float(table_data[idx][j]) > 3):  # Cc column
                cell.set_facecolor('#f0f0f0')
            elif j == 5 and "Poorly-graded" in table_data[idx][j]:
                cell.set_facecolor('#f0f0f0')

    # Add criteria text
    criteria_text = "GRADING CRITERIA:   Cu = D60/D10   •   Cc = (D30²)/(D10×D60)   •   Well-graded if: Cu > 4 (gravel), Cu > 6 (sand), and 1 < Cc < 3"
    ax_table.text(0.5, 0.02, criteria_text,
                 ha='center', va='top',
                 fontsize=9,
                 family='monospace',
                 transform=ax_table.transAxes)

    plt.tight_layout(h_pad=1.2)
    plt.show()

if __name__ == "__main__":
    # Example usage when running directly
    sample_data = [
        {
            'name': 'Fine Aggregate',
            'sizes': sieve_sizes,
            'values': fa_passing
        },
        {
            'name': 'Soil',
            'sizes': sieve_sizes,
            'values': soil_passing
        },
        {
            'name': 'Coarse Aggregate',
            'sizes': sieve_sizes,
            'values': ca_passing
        },
        {
            'name': 'Regraded Soil',
            'sizes': sieve_sizes,
            'values': regraded_soil
        }
    ]
    generate_plot(sample_data, use_color=True, interp_method='cubic',
                 null_method='interpolate', allow_extrapolation=False)