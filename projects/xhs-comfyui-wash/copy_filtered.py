import shutil
from pathlib import Path

# 源目录和目标目录
src_dir = Path(
    r"C:\Users\admin\Projects\xhs-image-filter\output\blogger_62235f03_v2\filtered"
)
dst_dir = Path(r"C:\Users\admin\Projects\xhs-image-filter\output\filtered")

# 创建目标目录
dst_dir.mkdir(parents=True, exist_ok=True)

# 复制所有png文件
png_files = list(src_dir.glob("*.png"))
print(f"找到 {len(png_files)} 个文件")

for f in png_files:
    shutil.copy2(f, dst_dir / f.name)
    print(f"复制: {f.name}")

print(f"\n完成！共复制 {len(png_files)} 个文件到 {dst_dir}")
