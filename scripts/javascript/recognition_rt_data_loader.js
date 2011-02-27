(function ($, jQuery, undefined) {
  var dataLoader;
  var tasks;
  var calibrationTasks;

  var allUrlParameters = ['numberOfAlphabets', 'exampleCharactersPerAlphabet',
    'sameTestCharactersPerAlphabet', 'differentTestCharactersPerAlphabet',
    'differentAlphabetTestCharactersPerAlphabet', 'distractWithAll',
    'pauseToFirstHint', 'pauseToSecondHint', 'pauseToExample', 'pauseToNoise',
    'pauseToTest', 'tasksPerFeedbackGroup', 'tasksPerWaitGroup', 
    'pauseToGroup', 'displayProgressBarDuringTask', 'random', 'characterSet',
    'trialsPerExperiment', 'fractionSame'];


  function retrieveData (loadData) {
    $.getJSON("../scripts/python/characters.py",
      urlParameters.getURLParameters(allUrlParameters),
      loadData);
  }

  function getTotalCount(data) {
    return data['tasks'].length * 7;
  }

  function onAccept() {
    calibrationTasks = new CalibrationTasks(tasks.startTasks);
    calibrationTasks.startTasks();
  };

  function onDoneTasks () {
    $('.tasks').hide();
    $('.post-task').show();
  }

  function doLoadData (data) {
    saveUrlParameters(data);
    tasks = new RecognitionRTTasks(data, data['tasks'].length, dataLoader,
        onDoneTasks);
    doneLoading();
  };
  notYetLoaded();

  function saveUrlParameters(data) {
    var hiddenInputs = $('#hidden-inputs');
    jQuery.each(allUrlParameters, function (index, parameter) {
      if (parameter in data)
        hiddenInputs.append(makeInput('url-parameter-' + parameter)
            .attr('value', data[parameter])
          );
    });
  }

  dataLoader = new DataLoader(retrieveData, getTotalCount, onAccept, doLoadData);
})($, jQuery);