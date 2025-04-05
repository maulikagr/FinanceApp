// Main JavaScript file for AI Finance App

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle mission completion
    const missionButtons = document.querySelectorAll('.complete-mission-btn');
    missionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const missionId = this.getAttribute('data-mission-id');
            
            fetch('/api/update_progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mission_id: missionId,
                    completed: true
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.missions_completed && data.missions_completed.includes(missionId)) {
                    alert('Mission completed! You earned ' + data.rewards_earned.coins + ' coins and ' + data.rewards_earned.experience + ' XP!');
                    location.reload();
                } else {
                    alert('Mission not completed. Check the requirements.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while completing the mission.');
            });
        });
    });

    // Handle challenge progress updates
    const challengeButtons = document.querySelectorAll('.update-challenge-btn');
    challengeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const challengeId = this.getAttribute('data-challenge-id');
            const progressValue = this.getAttribute('data-progress-value');
            
            fetch('/api/update_progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    challenge_id: challengeId,
                    progress: progressValue
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.challenges_completed && data.challenges_completed.includes(challengeId)) {
                    alert('Challenge completed! You earned ' + data.rewards_earned.coins + ' coins and ' + data.rewards_earned.experience + ' XP!');
                    location.reload();
                } else {
                    alert('Challenge progress updated!');
                    location.reload();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating the challenge.');
            });
        });
    });
}); 