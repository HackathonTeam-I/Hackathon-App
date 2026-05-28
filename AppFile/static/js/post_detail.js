document.addEventListener('DOMContentLoaded', () => {


    // 1. スライダー機能

    const postImagesDataElement = document.getElementById('postImagesData');
    const postImages = postImagesDataElement ? JSON.parse(postImagesDataElement.textContent) : [];

    const imageElement = document.querySelector('.detail-image');

    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');

    let currentIndex = 0;

    // 画像が2枚以上ある時のみクリックイベントを登録
    if (postImages.length > 1 && imageElement) {


        leftArrow?.addEventListener('click', () => {
            currentIndex = (currentIndex === 0) ? postImages.length - 1 : currentIndex - 1;
            imageElement.src = `/static/${postImages[currentIndex]}`;
        });

        rightArrow?.addEventListener('click', () => {
            currentIndex = (currentIndex === postImages.length - 1) ? 0 : currentIndex + 1;
            imageElement.src = `/static/${postImages[currentIndex]}`;
        });
    }

    // 2. モーダル ＆ 削除機能
    const deleteBtn = document.getElementById('showDeleteModalBtn');
    const deleteModal = document.getElementById('deleteModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    // モーダルの開閉
    deleteBtn?.addEventListener('click', () => {
        deleteModal?.classList.remove('hidden');
    });

    cancelDeleteBtn?.addEventListener('click', () => {
        deleteModal?.classList.add('hidden');
    });

    // 削除の非同期通信
    confirmDeleteBtn?.addEventListener('click', async () => {
        const postId = deleteBtn.getAttribute('data-post-id');
        const csrfToken = deleteBtn.getAttribute('data-csrf-token');

        try {
            const response = await fetch(`/api/admin/posts/${postId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.ok) {
                alert("削除に成功しました");
                window.location.href = deleteBtn.getAttribute('data-redirect-url');
            } else {
                deleteModal?.classList.add('hidden');
                alert("削除に失敗しました");
            }
        } catch (error) {
            console.error("通信エラー", error);
            deleteModal?.classList.add('hidden');
            alert("通信エラーが発生しました");
        }
    });
});