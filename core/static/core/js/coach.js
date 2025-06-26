  // This script mainly handles the dynamic loading of tables, arbiters, and players based on the selected hall, date, and time slot.
  // We couldn't use Django's built-in methods to handle this because we need to load data dynamically based on user input.
  document.addEventListener("DOMContentLoaded", function () {
    // Set the current date in the date input field
    const dateInput = document.getElementById("date");
    const today = new Date();
    const day = String(today.getDate()).padStart(2, "0");
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const year = today.getFullYear();
    const todayFormatted = `${day}-${month}-${year}`;
    dateInput.value = todayFormatted;

    // Get the HTML elements
    const hallSelect = document.getElementById("hall_id");
    const dateField = document.getElementById("date");
    const timeSlotField = document.getElementById("time_slot");
    const tableSelect = document.getElementById("table_id");
    const teamSelect = document.getElementById("team_id");

    // Function to load available tables based on hall, date and time slot
    function loadTables() {
      const hallId = hallSelect.value;
      const date = dateField.value;
      const timeSlot = timeSlotField.value;

      if (hallId && date && timeSlot) {
        tableSelect.disabled = false;
        tableSelect.innerHTML =
          '<option value="" selected disabled>Loading tables...</option>';
        fetch(
          `/coach?action=get_available_tables&hall_id=${hallId}&date=${date}&time_slot=${timeSlot}`
        )
          .then((response) => response.json())
          .then((data) => {
            tableSelect.innerHTML =
              '<option value="" selected disabled>-- Select Table --</option>';
            if (data.length > 0) {
              data.forEach((table) => {
                const option = document.createElement("option");
                option.value = table[0];
                option.textContent = `Table ${table[1]}`;
                tableSelect.appendChild(option);
              });
            } else {
              tableSelect.innerHTML =
                '<option value="" selected disabled>No available tables</option>';
            }
          })
          .catch((error) => {
            console.error("Error loading tables:", error);
            tableSelect.innerHTML =
              '<option value="" selected disabled>Error loading tables</option>';
          });
      }
    }

    // Attach event listeners for table loading
    hallSelect.addEventListener("change", loadTables);
    dateField.addEventListener("change", loadTables);
    timeSlotField.addEventListener("change", loadTables);

    // Function to load available arbiters based on date and time slot
    function loadArbiters() {
      const date = dateField.value;
      const timeSlot = timeSlotField.value;
      const arbiterSelect = document.getElementById("arbiter_username");

      if (date && timeSlot) {
        arbiterSelect.disabled = false;
        arbiterSelect.innerHTML =
          '<option value="" selected disabled>Loading arbiters...</option>';
        fetch(
          `/coach?action=get_available_arbiters&date=${date}&time_slot=${timeSlot}`
        )
          .then((response) => response.json())
          .then((data) => {
            arbiterSelect.innerHTML =
              '<option value="" selected disabled>-- Select Arbiter --</option>';
            if (data.length > 0) {
              data.forEach((arbiter) => {
                const option = document.createElement("option");
                option.value = arbiter[0];
                option.textContent = arbiter[1];
                arbiterSelect.appendChild(option);
              });
            } else {
              arbiterSelect.innerHTML =
                '<option value="" selected disabled>No available arbiters</option>';
            }
          })
          .catch((error) => {
            console.error("Error loading arbiters:", error);
          });
      }
    }

    // Attach event listeners for arbiter loading
    dateField.addEventListener("change", loadArbiters);
    timeSlotField.addEventListener("change", loadArbiters);

    // Function to load available players based on team, date and time slot
    function loadTeamPlayers() {
      const teamId = teamSelect.value;
      const date = dateField.value;
      const timeSlot = timeSlotField.value;
      const playerSelect = document.getElementById("player_username");

      if (teamId && date && timeSlot) {
        playerSelect.disabled = false;
        playerSelect.innerHTML =
          '<option value="" selected disabled>Loading players...</option>';
        fetch(
          `/coach?action=get_available_team_players&team_id=${teamId}&date=${date}&time_slot=${timeSlot}`
        )
          .then((response) => response.json())
          .then((data) => {
            playerSelect.innerHTML =
              '<option value="" selected disabled>-- Select Player --</option>';
            if (data.length > 0) {
              data.forEach((player) => {
                const option = document.createElement("option");
                option.value = player[0];
                option.textContent = player[1];
                playerSelect.appendChild(option);
              });
            } else {
              playerSelect.innerHTML =
                '<option value="" selected disabled>No available players</option>';
            }
          })
          .catch((error) => {
            console.error("Error loading players:", error);
          });
      }
    }

    // Attach event listeners for player loading
    dateField.addEventListener("change", loadTeamPlayers);
    timeSlotField.addEventListener("change", loadTeamPlayers);

    // Load players on page load if date and time are set
    if (dateField.value && timeSlotField.value) {
      loadTeamPlayers();
    }

    // Delete match confirmation
    const deleteForms = document.querySelectorAll(".delete-match-form");
    deleteForms.forEach((form) => {
      form.addEventListener("submit", function (event) {
        if (!confirm("Are you sure you want to delete this match?")) {
          event.preventDefault();
        }
      });
    });

    // Load available players for my assigned matches that don't have a black player yet
    document.querySelectorAll(".player-select").forEach((select) => {
      const teamId = teamSelect.value;
      const date = select.dataset.date;
      const timeSlot = select.dataset.timeSlot;

      if (teamId && date && timeSlot) {
        fetch(
          `/coach?action=get_available_players_for_team&team_id=${teamId}&date=${date}&time_slot=${timeSlot}`
        )
          .then((response) => response.json())
          .then((data) => {
            if (data.length > 0) {
              data.forEach((player) => {
                const option = document.createElement("option");
                option.value = player[0];
                option.textContent = player[1];
                select.appendChild(option);
              });
            } else {
              select.innerHTML =
                '<option value="" selected disabled>No available players</option>';
              const assignBtn = select.nextElementSibling;
              if (assignBtn) {
                assignBtn.disabled = true;
              }
            }
          })
          .catch((error) => {
            console.error("Error loading players:", error);
          });
      }
    });
  });