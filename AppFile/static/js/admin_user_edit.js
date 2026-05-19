document.addEventListener('DOMContentLoaded', () => {
    //HTMLから要素を取得
    const updateBtn = document.getElementById('updateBtn');
    const deleteBtn = document.getElementById('deleteBtn');

    const userId = document.getElementById('userId').value;
    const csrfToken = document.getElementById('csrf_token').value;

    //更新ボタン（PATCHメソッド）が押されたとき
    updateBtn.addEventListener('click', async () => {
        //送信データを作成
        const updateData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            department: document.getElementById('department').value,
        };

        //パスワードは変更があったときのみ
        const password = document.getElementById('password').value;
        if (password) {
            updateData.password = password;
        }

        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken  //csrf認証
                },
                body: JSON.stringify(updateData) //データをJSON形式にして送る
            });

            if (response.ok) {
                alert('ユーザ情報を更新しました')
                window.location.href = '/admin/users'; //一覧へ戻る
            } else {
                alert('更新に失敗しました。入力内容を確認してください。');
            }
        } catch (error) {
            console.error('通信エラー:', error);
            alert('通信エラーが発生しました');
        }
    });

    //削除ボタンが押されたとき
    deleteBtn.addEventListener('click', async () => {
        //確認ポップアップ
        if (!confirm('本当にこのユーザを削除してもよろしいですか？\nこの操作は取り消せません。')) {
            return; //いいえを押した際に処理はストップ
        }

        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            if (response.ok) {
                alert('ユーザを削除しました。');
                window.location.href = '/admin/users'; //一覧へ戻る
            } else {
                alert('削除に失敗しました。');
            }
        } catch (error) {
            console.error('通信エラー:', error);
            alert('通信エラーが発生しました。');
        }
    });
});