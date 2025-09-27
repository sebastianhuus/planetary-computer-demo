I wanted to try the Planetary Computer from Microsoft, and I tried following some documentation from their own docs and examples. However, it didn't work because it assumed we were using a Dask gateway cluster that was hosted by Microsoft, which was discontinued in 2024.

So, I had to make a few adaptations to make it work with local processing instead of doing remote processing. I also reduced the complexity of the satellite image so my computer wouldn't die. 

Original docs:
https://planetarycomputer.microsoft.com/docs/tutorials/cloudless-mosaic-sentinel2/