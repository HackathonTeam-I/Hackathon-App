document.addEventListener('DOMContentLoaded', () => {
    const deleteBtn = document.getElementById('showDeleteModalBtn');
    const deleteModal = document.getElementById('deleteModal');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');

    //削除ボタンを押してモーダルが起動
    if (deleteBtn) {
        deleteBtn.addEventListener('click', () => {
            deleteModal.classList.remove('hidden'); //hiddenクラスを削除してモーダルが見えるようにする
        });
    }

    //「いいえ」ボタンを押してモーダルを閉じる
    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            deleteModal.classList.add('hidden');
        });
    }

    // 「はい」を押してDELETEリクエストを送信
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', async () => {

            const postId = deleteBtn.getAttribute('data-post-id');

            try {
                // Fetch APIでDELETEメソッドを送信
                const responce = await fetch(`api/admin/posts/${postId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'addlication/json'
                    }
                });

                if (responce.ok) {
                    //削除成功により投稿一覧へ遷移する
                    alert("削除に成功しました");
                    window.location.href = "/posts";
                } else {
                    alert("削除に失敗しました");
                }
            } catch (error) {
                console.error("通信エラー", error);
                alert("通信エラーが発生しました");
            } finally {
                //最期は必ずモーダルを閉じる
                deleteModal.classList.add('hidden');
            }
        });
    }
});