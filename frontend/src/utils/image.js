// 업로드 이미지를 긴 변 기준으로 줄여 JPEG data URL로 (프로필·커버 저장용, 약 1MB 이하)
export async function fileToDataUrl(file, maxSide = 1400, quality = 0.85) {
  if (!/^image\/(jpeg|png|webp)$/.test(file.type)) throw new Error('JPG/PNG/WEBP 이미지만 올릴 수 있어요.')
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height))
  const canvas = Object.assign(document.createElement('canvas'), { width: Math.round(bitmap.width * scale), height: Math.round(bitmap.height * scale) })
  canvas.getContext('2d').drawImage(bitmap, 0, 0, canvas.width, canvas.height)
  let url = canvas.toDataURL('image/jpeg', quality)
  for (let q = quality - 0.15; url.length > 1_400_000 && q > 0.3; q -= 0.15) url = canvas.toDataURL('image/jpeg', q)
  return url
}
