"""A sparse BC image is made with the usage its sparse residency was checked for.

texture_create asks vkGetPhysicalDeviceSparseImageFormatProperties whether a too-big 2D array can be sparse, and for a BC
format it asks with TRANSFER_SRC | TRANSFER_DST | SAMPLED only. The image was then created with x.usage, which for BC
formats may also hold STORAGE and COLOR_ATTACHMENT (the raw block views): a combination the driver was never asked about.
AMD's driver refused it, and the texture was lost. Now the sparse BC image drops those two usages before it is made, as a
compressed image the driver refuses does below, and its raw views are not made.

python -I -B tests/test_sparse_bc_usage.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
	src = (ROOT / "gpu" / "vk" / "vk_texture.cpp").read_text(encoding="utf-8")
	ask = src.find("vkGetPhysicalDeviceSparseImageFormatProperties(")
	if ask < 0:
		raise SystemExit("sparse residency is no longer asked in vk_texture.cpp: this test needs updating")
	asked = src[src.rfind("VkImageUsageFlags u", 0, ask):ask]
	if "if (!is_bc(x.format)) u |= VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT | VK_IMAGE_USAGE_STORAGE_BIT;" not in asked:
		raise SystemExit("the usage sparse residency is asked with changed: this test needs updating")
	flag = src.find("ci.flags |= VK_IMAGE_CREATE_SPARSE_BINDING_BIT | VK_IMAGE_CREATE_SPARSE_RESIDENCY_BIT;")
	make = src.find("vkCreateImage(dev.device, &ci", flag)
	if flag < 0 or make < 0:
		raise SystemExit("the sparse image is no longer made there: this test needs updating")
	between = src[flag:make]
	if ("is_bc(x.format)" not in between or "~(VK_IMAGE_USAGE_STORAGE_BIT | VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT)" not in between
			or "x.usage = ci.usage" not in between):
		raise SystemExit("a sparse BC image is made with STORAGE/COLOR_ATTACHMENT, which its sparse residency was not asked with")
	print("a sparse BC image is made with the usage its sparse residency was asked with")


if __name__ == "__main__":
	main()
