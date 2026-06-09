from scipy.io import netcdf
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

# Create plot
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)
# Data is spaced from 1e-6 to 1e-5
levels = np.linspace(1e-6, 1e-5, 11)
# TBA
image1 = axes[0].contourf(lat, plev, O3_time, levels=levels, cmap='turbo', extend='both')
# Setting title of plot and y label name
axes[0].set_title('O3 Laschamp annual mean')
axes[0].set_ylabel('Altitude Pa')

image2 = axes[1].contourf(lat, plev, O3_time_ref, levels=levels, cmap='turbo', extend='both')
axes[1].set_title('O3 Ref annual mean')
axes[1].set_ylabel('Altitude Pa')

# Creating image colorbar for Laschamp
fig.colorbar(image1, ax=axes[0], orientation='vertical', format='%.0e')
# Creating colorbar for Reference
fig.colorbar(image2, ax=axes[1], orientation='vertical', format='%.0e')

# Setting x and y axis limits, y scale, and x label name for all plots
for a in axes:
  a.set_yscale('log')
  a.set_xlabel('Latitude')
  a.set_ylim(1e5, 1e0)
  a.set_xlim(-90, 90)

# Show plot
plt.show()
