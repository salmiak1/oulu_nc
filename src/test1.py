from scipy.io import netcdf
import scipy.stats as stats
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import xarray as xr

# Open netCDF source file for Laschamp
netcdf_file = '../../oulu_cdf_catalog/socol4_gs1_ss0_chem_mm_zm_2308-2399.nc'
xrds = xr.open_dataset(netcdf_file)
# Getting O3 data
O3 = xrds.O3_m 

# Getting annual mean by time and longitude to eliminate dependency
O3_time = O3.mean(dim=['time', 'lon'])

# Getting latitude and altitude coordinates
lat = O3.lat
plev = O3.plev

# Open netCDF source file for Reference O3 data
netcdf_file_ref = '../../oulu_cdf_catalog/O3_all_years.nc'
xrds = xr.open_dataset(netcdf_file_ref)
# Getting O3 data
O3_ref = xrds.O3_m 

# Getting annual mean by time and longitude to eliminate dependency
O3_time_ref = O3_ref.mean(dim=['time', 'lon'])
# O3 Lat and plev for ref are identical to lat and ref for Laschamp!

# Statistical analysis:
# Calculate percent difference according to formula (Laschamp - Reference)/ Reference
percent_diff = ((O3_time - O3_time_ref) / O3_time_ref) * 100
# Getting the reference and laschamp annual mean by longitude, so we can eliminate dependency
O3_lon_ref = O3_ref.mean(dim='lon')
O3_lon = O3.mean(dim='lon')
# Performing the Welch t-test
t_stats, welch_test_p = stats.ttest_ind(O3_lon.values, O3_lon_ref.values, axis=0, equal_var=False)
# Making sure the p values are p_val < 0.05
significant_mask = welch_test_p < 0.05
# Getting a new percent difference where only the p < 0.05 are applied! Everything not significantly different is NaN 
percent_diff_p_val = np.where(significant_mask, percent_diff.values, np.nan)

# Create plot
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
# Data is spaced from 1e-6 to 1e-5
levels = np.linspace(1e-6, 1e-5, 11)
# Creating the color plot for Laschamp
image1 = axes[0].contourf(lat, plev, O3_time, levels=levels, cmap='turbo', extend='both')
# Setting title of plot and y label name
axes[0].set_title('O3 Laschamp annual mean')

# Creating the color plot for Reference and setting title
image2 = axes[1].contourf(lat, plev, O3_time_ref, levels=levels, cmap='turbo', extend='both')
axes[1].set_title('O3 Ref annual mean')

# Spacing the data from -20 to 50 for the statistical analysis plot
levels_diff = np.linspace(-20, 50, 15)
# Creating the color plot for statistical analysis and setting title
image3 = axes[2].contourf(lat, plev, percent_diff_p_val, levels=levels_diff, cmap='jet', extend='both')
axes[2].set_title('% difference (significant only, Welch t-test, p<0.05)')


# Creating image colorbar for Laschamp
fig.colorbar(image1, ax=axes[0], orientation='vertical', format='%.0e')
# Creating colorbar for Reference
fig.colorbar(image2, ax=axes[1], orientation='vertical', format='%.0e')
# Creating colorbar for statistical analysis plot
fig.colorbar(image3, ax=axes[2], orientation='vertical', format='%.0e')

# Setting x and y axis limits, y scale, and x label name for all plots
for a in axes:
  a.set_yscale('log')
  a.set_xlabel('Latitude')
  a.set_ylabel('Altitude Pa')
  a.set_ylim(1e5, 1e0)
  a.set_xlim(-90, 90)

# Show plot
#plt.tight_layout()
#plt.show()

# Save plot as .png
#plt.savefig('O3_analysis.png')

# Create the significant percent difference as an xarray object, this is done so later we can xr.sel() to zoom in
percent_diff_p_val_xr = xr.DataArray(data=percent_diff_p_val, dims=['plev', 'lat'], coords={'plev': plev, 'lat': lat})
# Select the top part, corresponding to the high altitude polar region.
top_zoom = percent_diff_p_val_xr.sel(lat=slice(-65, -85), plev=slice(1e0, 1e2))
# Getting top region's lat and plev
top_lat = top_zoom.lat
top_plev = top_zoom.plev
# Create plot for the top zoom
fig, axess = plt.subplots(figsize=(6, 5))
# Create image for top zoom
image4 = axess.contourf(top_lat, top_plev, top_zoom, levels=levels_diff, cmap='jet', extend='both')
# Setting y scale, logarithmic
axess.set_yscale('log')
# Setting y limit for plot
axess.set_ylim(top_plev.max().item(), top_plev.min().item())
# Setting x limit for plot
axess.set_xlim(top_zoom.lat.min().item(), top_zoom.lat.max().item())
# Create colorbar for top zoom
fig.colorbar(image4, ax=axess, orientation='vertical', format='%.0e')
# Setting x and y labels for plot, and plot title
axess.set_xlabel('Latitude')
axess.set_ylabel('Pressure Pa')
axess.set_title('% difference, Welch t-test, zoom top left')
# Display plot
plt.show()