document.addEventListener('DOMContentLoaded', function () {
    const userDomain = 'Aaaa'; // Замените 'Aaaa' на актуальное доменное имя пользователя.

    // Загрузка аватарок
    for (let i = 1; i <= 3; i++) {
        document.getElementById('avatar' + i).style.backgroundImage = 'url("https://raw.githubusercontent.com/mrwind13/NOTGAME13/main/' + userDomain + '_' + i + '.jpg")';
    }

    // Загрузка данных из файла на GitHub
    fetch('https://raw.githubusercontent.com/mrwind13/NOTGAME13/main/' + userDomain + '_info.txt')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.text();
        })
        .then(data => {
            const lines = data.split('\n');
            document.getElementById('nickname').innerText = lines.find(line => line.startsWith('nickname =')).split('=')[1].trim();
            const links = lines.filter(line => line.includes('social_link'));
            const customLinks = lines.filter(line => line.includes('custom_link'));

            // Присваивание ссылок и изображений кнопкам социальных сетей
            document.getElementById('social1').innerHTML = '<a href="' + links[0].split('=')[1].trim() + '" target="_blank"><img src="https://static.tildacdn.com/tild3538-6130-4332-a536-626237646234/svg_1723200719247.svg" alt="Social 1" style="height: auto; width: 50%;"></a>';
            document.getElementById('social2').innerHTML = '<a href="' + links[1].split('=')[1].trim() + '" target="_blank"><img src="https://static.tildacdn.com/tild6333-6332-4734-b834-336265393963/Vector.svg" alt="Social 2" style="height: auto; width: 50%;"></a>';
            document.getElementById('social3').innerHTML = '<a href="' + links[2].split('=')[1].trim() + '" target="_blank"><img src="https://static.tildacdn.com/tild3138-3361-4963-b036-323964366430/svg_1723200676248.svg" alt="Social 3" style="height: auto; width: 50%;"></a>';

            // Присваивание ссылок кастомным кнопкам
            document.getElementById('custom1').innerHTML = '<a href="' + customLinks[0].split('=')[1].trim() + '" target="_blank">Custom Button 1</a>';
            document.getElementById('custom2').innerHTML = '<a href="' + customLinks[1].split('=')[1].trim() + '" target="_blank">Custom Button 2</a>';
        })
        .catch(error => console.error('Ошибка при загрузке файла:', error));
});