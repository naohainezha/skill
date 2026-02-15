# Step 3: Check Results

## Output Location

```
D:\output\xitu\
```

## Check Commands

```bash
# Count output files
ls "D:/output/xitu/" | wc -l

# Check queue status (0 remaining = done)
curl -s http://192.168.11.158:8188/queue
```

## Verify

- Output file count matches input count
- Files are non-zero size
- Images open correctly

## Optional: Copy to processed

```bash
cp "D:/output/xitu/"*.png "C:/Users/admin/Projects/xhs-image-filter/output/processed/"
```
