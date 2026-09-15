// lib/translations.ts - Complete trilingual dictionary for AgriSmart AI

import { LanguageCode } from '@/types/api';

export interface Translations {
  // App Header & Branding
  appName: string;
  appTagline: string;
  backendOnline: string;
  backendOffline: string;
  checkingConnection: string;

  // Navigation
  tabAssistant: string;
  tabDisease: string;
  tabAdvisory: string;
  tabWeather: string;

  // AI Kisan Assistant
  assistantTitle: string;
  assistantSubtitle: string;
  askPlaceholder: string;
  sendBtn: string;
  listeningNow: string;
  voiceTooltip: string;
  speechNotSupported: string;
  clearChat: string;
  followUpTitle: string;
  sourcesTitle: string;
  confidenceLabel: string;
  welcomeMessage: string;
  sampleQuestions: string[];

  // Crop Disease Doctor
  diseaseTitle: string;
  diseaseSubtitle: string;
  openCameraBtn: string;
  capturePhotoBtn: string;
  retakeBtn: string;
  switchCameraBtn: string;
  cameraGuide: string;
  orUploadFile: string;
  dropImageHere: string;
  browseFiles: string;
  analyzingImage: string;
  analyzeDiseaseBtn: string;
  diagnosisResult: string;
  cropLabel: string;
  severityLabel: string;
  statusHealthy: string;
  statusDiseased: string;
  precautionsTitle: string;
  recommendationsTitle: string;
  askAssistantAboutDisease: string;
  cameraPermissionDenied: string;
  noCameraFound: string;

  // Smart Irrigation & Advisory
  advisoryTitle: string;
  advisorySubtitle: string;
  cropNameLabel: string;
  growthStageLabel: string;
  soilTypeLabel: string;
  phLabel: string;
  moistureLabel: string;
  tempLabel: string;
  rainProbLabel: string;
  currentMethodLabel: string;
  getAdvisoryBtn: string;
  calculatingAdvisory: string;
  shouldIrrigateToday: string;
  irrigateYes: string;
  irrigateNo: string;
  sustainabilityScore: string;
  recommendedMethod: string;
  timetableTitle: string;
  dayLabel: string;
  durationLabel: string;
  waterVolumeLabel: string;
  notesLabel: string;
  soilHealthNotes: string;
  riskFlagsTitle: string;
  actionableTipsTitle: string;

  // Weather Risk Forecast
  weatherTitle: string;
  weatherSubtitle: string;
  locationLabel: string;
  locationPlaceholder: string;
  daysAheadLabel: string;
  getForecastBtn: string;
  fetchingWeather: string;
  overallRiskTitle: string;
  riskLow: string;
  riskModerate: string;
  riskHigh: string;
  riskSevere: string;
  dailyForecastTitle: string;
  rainfallLabel: string;
  humidityLabel: string;
  windLabel: string;
  weatherRecommendations: string;
  quickLocations: string[];

  // Common UI
  loading: string;
  error: string;
  dismiss: string;
  retry: string;
  success: string;
}

export const translations: Record<LanguageCode, Translations> = {
  en: {
    appName: 'AgriSmart AI',
    appTagline: 'Precision Farming & Smart Kisan Intelligence',
    backendOnline: 'Connected',
    backendOffline: 'Offline',
    checkingConnection: 'Checking...',

    tabAssistant: 'AI Kisan Assistant',
    tabDisease: 'Crop Disease Doctor',
    tabAdvisory: 'Smart Irrigation',
    tabWeather: 'Weather Risk',

    assistantTitle: 'AI Kisan Assistant',
    assistantSubtitle: 'Ask farming questions in English, Hindi, or Gujarati with live voice support',
    askPlaceholder: 'Ask anything about crops, pests, fertilizers, or prices...',
    sendBtn: 'Send Query',
    listeningNow: 'Listening to your voice...',
    voiceTooltip: 'Click to speak (English)',
    speechNotSupported: 'Web Speech API is not supported in your browser. Please use Chrome or Edge.',
    clearChat: 'Clear Conversation',
    followUpTitle: 'Suggested Questions',
    sourcesTitle: 'Agronomic Sources',
    confidenceLabel: 'Confidence',
    welcomeMessage: 'Namaste! I am your AI Kisan Assistant. How can I help with your field, crops, or farming practices today?',
    sampleQuestions: [
      'My tomato leaves are turning yellow with black spots. What should I do?',
      'What is the best irrigation schedule for flowering wheat?',
      'How do I prevent fungal root rot during rainy season?',
    ],

    diseaseTitle: 'Crop Disease Doctor',
    diseaseSubtitle: 'Instant AI leaf pathology with live camera & ICAR-certified treatment plans',
    openCameraBtn: 'Open Camera',
    capturePhotoBtn: 'Capture Leaf Photo',
    retakeBtn: 'Retake Photo',
    switchCameraBtn: 'Switch Camera',
    cameraGuide: 'Position the infected leaf clearly inside the viewfinder',
    orUploadFile: 'Or upload a saved leaf photo',
    dropImageHere: 'Drop leaf image here or',
    browseFiles: 'browse files',
    analyzingImage: 'Analyzing leaf with AI vision...',
    analyzeDiseaseBtn: 'Diagnose Disease',
    diagnosisResult: 'Diagnostic Report',
    cropLabel: 'Crop',
    severityLabel: 'Severity',
    statusHealthy: 'Healthy Crop',
    statusDiseased: 'Infection Detected',
    precautionsTitle: 'Step-by-Step Precautions',
    recommendationsTitle: 'Actionable Treatments',
    askAssistantAboutDisease: 'Ask Assistant About This Disease',
    cameraPermissionDenied: 'Camera access was denied. Please allow camera permissions in browser settings.',
    noCameraFound: 'No camera hardware found on this device.',

    advisoryTitle: 'Smart Irrigation & Advisory',
    advisorySubtitle: 'Optimize water efficiency and field sustainability with sensor-driven recommendations',
    cropNameLabel: 'Crop Name',
    growthStageLabel: 'Growth Stage',
    soilTypeLabel: 'Soil Type',
    phLabel: 'Soil pH',
    moistureLabel: 'Soil Moisture (%)',
    tempLabel: 'Field Temperature (°C)',
    rainProbLabel: '24-Hour Rain Probability (%)',
    currentMethodLabel: 'Current Irrigation Method',
    getAdvisoryBtn: 'Generate Irrigation Plan',
    calculatingAdvisory: 'Calculating soil water balance...',
    shouldIrrigateToday: 'Irrigation Needed Today?',
    irrigateYes: 'YES — Irrigation Recommended',
    irrigateNo: 'NO — Soil Moisture Is Sufficient',
    sustainabilityScore: 'Sustainability Index',
    recommendedMethod: 'Best Irrigation Method',
    timetableTitle: '3-Day Irrigation Timetable',
    dayLabel: 'Day',
    durationLabel: 'Duration (Minutes)',
    waterVolumeLabel: 'Water Volume',
    notesLabel: 'Guidance',
    soilHealthNotes: 'Soil Health Observations',
    riskFlagsTitle: 'Agronomic Risk Flags',
    actionableTipsTitle: 'Farmer Action Checklist',

    weatherTitle: 'Weather Risk Forecast',
    weatherSubtitle: 'Multi-day agricultural weather risk analysis & proactive crop advisories',
    locationLabel: 'Field Location',
    locationPlaceholder: 'Enter city or region (e.g., Ahmedabad, Hyderabad, Pune)',
    daysAheadLabel: 'Forecast Window (Days)',
    getForecastBtn: 'Check Weather Risk',
    fetchingWeather: 'Fetching weather risk assessment...',
    overallRiskTitle: 'Overall Weather Risk Level',
    riskLow: 'Low Risk',
    riskModerate: 'Moderate Risk',
    riskHigh: 'High Risk',
    riskSevere: 'Severe Risk',
    dailyForecastTitle: 'Daily Forecast & Threat Index',
    rainfallLabel: 'Rainfall',
    humidityLabel: 'Humidity',
    windLabel: 'Wind',
    weatherRecommendations: 'Weather-Driven Crop Advisory',
    quickLocations: ['Ahmedabad', 'Rajkot', 'Surat', 'Hyderabad', 'Pune', 'Ludhiana'],

    loading: 'Loading...',
    error: 'An error occurred',
    dismiss: 'Dismiss',
    retry: 'Retry',
    success: 'Success',
  },

  hi: {
    appName: 'एग्रीस्मार्ट AI',
    appTagline: 'सटीक कृषि और स्मार्ट किसान बुद्धिमत्ता',
    backendOnline: 'सक्रिय (ऑनलाइन)',
    backendOffline: 'ऑफ़लाइन',
    checkingConnection: 'जांच जारी...',

    tabAssistant: 'AI किसान सहायक',
    tabDisease: 'फसल रोग डॉक्टर',
    tabAdvisory: 'स्मार्ट सिंचाई',
    tabWeather: 'मौसम जोखिम',

    assistantTitle: 'AI किसान सहायक',
    assistantSubtitle: 'लाइव आवाज़ समर्थन के साथ हिंदी, गुजराती या अंग्रेजी में कृषि सलाह पाएं',
    askPlaceholder: 'फसलों, कीटों, खादों या कृषि उत्पादों के बारे में कुछ भी पूछें...',
    sendBtn: 'प्रश्न भेजें',
    listeningNow: 'आपकी आवाज़ सुनी जा रही है...',
    voiceTooltip: 'बोलने के लिए माइक दबाएं (हिंदी)',
    speechNotSupported: 'आपके ब्राउज़र में वेब स्पीच API समर्थित नहीं है। कृपया Chrome या Edge का उपयोग करें।',
    clearChat: 'बातचीत साफ़ करें',
    followUpTitle: 'सुझाए गए प्रश्न',
    sourcesTitle: 'कृषि विज्ञान स्रोत',
    confidenceLabel: 'सटीकता विश्वास',
    welcomeMessage: 'नमस्ते किसान भाई! मैं आपका AI किसान सहायक हूँ। आज मैं आपकी फसल, खेत या सिंचाई में कैसे सहायता कर सकता हूँ?',
    sampleQuestions: [
      'टमाटर के पत्तों पर काले धब्बे आ रहे हैं, क्या उपाय करें?',
      'गेहूं में फूल आने पर सिंचाई का सही समय क्या है?',
      'बरसात के मौसम में फफूंद से बचाव कैसे करें?',
    ],

    diseaseTitle: 'फसल रोग डॉक्टर',
    diseaseSubtitle: 'लाइव कैमरा और ICAR-प्रमाणित उपचार योजनाओं के साथ त्वरित AI पत्ता निदान',
    openCameraBtn: 'कैमरा खोलें',
    capturePhotoBtn: 'पत्ते की फोटो खींचें',
    retakeBtn: 'दोबारा फोटो लें',
    switchCameraBtn: 'कैमरा बदलें',
    cameraGuide: 'संक्रमित पत्ते को कैमरे के बीच में साफ़ रखें',
    orUploadFile: 'या गैलरी से पत्ते की फोटो चुनें',
    dropImageHere: 'यहाँ फोटो डालें या',
    browseFiles: 'फ़ाइल चुनें',
    analyzingImage: 'AI द्वारा पत्ते की जांच की जा रही है...',
    analyzeDiseaseBtn: 'रोग का निदान करें',
    diagnosisResult: 'रोग निदान रिपोर्ट',
    cropLabel: 'फसल',
    severityLabel: 'गंभीरता',
    statusHealthy: 'स्वस्थ फसल',
    statusDiseased: 'रोग का संक्रमण मिला',
    precautionsTitle: 'क्रमबद्ध सावधानियां',
    recommendationsTitle: 'आवश्यक उपचार कदम',
    askAssistantAboutDisease: 'इस रोग के बारे में किसान सहायक से पूछें',
    cameraPermissionDenied: 'कैमरा अनुमति अस्वीकार कर दी गई। कृपया ब्राउज़र सेटिंग्स में अनुमति दें।',
    noCameraFound: 'इस डिवाइस पर कोई कैमरा नहीं मिला।',

    advisoryTitle: 'स्मार्ट सिंचाई और कृषि सलाह',
    advisorySubtitle: 'सेंसर आधारित सिफारिशों के साथ पानी की बचत और खेत की उत्पादकता बढ़ाएं',
    cropNameLabel: 'फसल का नाम',
    growthStageLabel: 'विकास चरण',
    soilTypeLabel: 'मिट्टी का प्रकार',
    phLabel: 'मिट्टी का pH',
    moistureLabel: 'मिट्टी की नमी (%)',
    tempLabel: 'खेत का तापमान (°C)',
    rainProbLabel: '24 घंटे में बारिश की संभावना (%)',
    currentMethodLabel: 'वर्तमान सिंचाई विधि',
    getAdvisoryBtn: 'सिंचाई योजना प्राप्त करें',
    calculatingAdvisory: 'मिट्टी में जल संतुलन की गणना की जा रही है...',
    shouldIrrigateToday: 'क्या आज सिंचाई की आवश्यकता है?',
    irrigateYes: 'हाँ — आज सिंचाई करने की सलाह दी जाती है',
    irrigateNo: 'नहीं — मिट्टी में पर्याप्त नमी उपलब्ध है',
    sustainabilityScore: 'स्थिरता सूचकांक',
    recommendedMethod: 'उत्कृष्ट सिंचाई विधि',
    timetableTitle: '3-दिवसीय सिंचाई समय-सारणी',
    dayLabel: 'दिन',
    durationLabel: 'समय (मिनट)',
    waterVolumeLabel: 'पानी की मात्रा',
    notesLabel: 'मार्गदर्शन',
    soilHealthNotes: 'मिट्टी स्वास्थ्य विश्लेषण',
    riskFlagsTitle: 'कृषि जोखिम चेतावनी',
    actionableTipsTitle: 'किसान कार्य सूची',

    weatherTitle: 'मौसम जोखिम पूर्वानुमान',
    weatherSubtitle: 'बहु-दिवसीय कृषि मौसम जोखिम विश्लेषण और अग्रिम फसल सलाह',
    locationLabel: 'खेत का स्थान / शहर',
    locationPlaceholder: 'शहर या ज़िले का नाम दर्ज करें (उदा. अहमदाबाद, हैदराबाद, पुणे)',
    daysAheadLabel: 'पूर्वानुमान दिन संख्या',
    getForecastBtn: 'मौसम जोखिम जांचें',
    fetchingWeather: 'मौसम डेटा प्राप्त किया जा रहा है...',
    overallRiskTitle: 'कुल मौसम जोखिम स्तर',
    riskLow: 'कम जोखिम',
    riskModerate: 'मध्यम जोखिम',
    riskHigh: 'उच्च जोखिम',
    riskSevere: 'गंभीर जोखिम',
    dailyForecastTitle: 'दैनिक पूर्वानुमान और जोखिम सूचकांक',
    rainfallLabel: 'वर्षा',
    humidityLabel: 'नमी',
    windLabel: 'हवा',
    weatherRecommendations: 'मौसम अनुकूल कृषि सलाह',
    quickLocations: ['अहमदाबाद', 'राजकोट', 'सूरत', 'हैदराबाद', 'पुणे', 'लुधियाना'],

    loading: 'लोड हो रहा है...',
    error: 'एक त्रुटि हुई',
    dismiss: 'हटाएं',
    retry: 'पुनः प्रयास करें',
    success: 'सफल',
  },

  gu: {
    appName: 'એગ્રીસ્માર્ટ AI',
    appTagline: 'ચોક્કસ ખેતી અને સ્માર્ટ કિસાન બુદ્ધિમત્તા',
    backendOnline: 'જોડાયેલ (ઓનલાઇન)',
    backendOffline: 'ઓફલાઇન',
    checkingConnection: 'તપાસી રહ્યું છે...',

    tabAssistant: 'AI કિસાન સહાયક',
    tabDisease: 'પાક રોગ ડોક્ટર',
    tabAdvisory: 'સ્માર્ટ પિયત સલાહ',
    tabWeather: 'હવામાન જોખમ',

    assistantTitle: 'AI કિસાન સહાયક',
    assistantSubtitle: 'લાઈવ વૉઇસ સપોર્ટ સાથે ગુજરાતી, હિન્દી કે અંગ્રેજીમાં ખેતી સલાહ મેળવો',
    askPlaceholder: 'પાક, જીવાત, ખાતર કે દવાઓ વિશે કંઈ પણ પૂછો...',
    sendBtn: 'પ્રશ્ન પૂછો',
    listeningNow: 'તમારો અવાજ સાંભળી રહ્યું છે...',
    voiceTooltip: 'બોલવા માટે માઇક દબાવો (ગુજરાતી)',
    speechNotSupported: 'તમારા બ્રાઉઝરમાં વેબ સ્પીચ સપોર્ટ નથી. કૃપા કરીને Chrome અથવા Edge વાપરો.',
    clearChat: 'વાતચીત સાફ કરો',
    followUpTitle: 'સૂચવેલા પ્રશ્નો',
    sourcesTitle: 'કૃષિ વિજ્ઞાન સંદર્ભ',
    confidenceLabel: 'ચોકસાઈ સ્કોર',
    welcomeMessage: 'નમસ્તે ખેડૂત મિત્ર! હું તમારો AI કિસાન સહાયક છું. આજે તમારા ખેતર કે પાક માટે હું શી મદદ કરી શકું?',
    sampleQuestions: [
      'ટામેટાના પાંદડા પીળા પડી રહ્યા છે અને ડાઘા છે, શું કરવું?',
      'કપાસમાં ફૂલ-ભમરી અવસ્થાએ કેટલું પાણી આપવું?',
      'ચોમાસામાં ફૂગજન્ય રોગોથી પાકનું રક્ષણ કેવી રીતે કરવું?',
    ],

    diseaseTitle: 'પાક રોગ ડોક્ટર',
    diseaseSubtitle: 'લાઈવ કૅમેરા અને ICAR પ્રમાણિત ઉપચાર પદ્ધતિ સાથે ત્વરિત AI રોગ નિદાન',
    openCameraBtn: 'કૅમેરો શરૂ કરો',
    capturePhotoBtn: 'પાંદડાનો ફોટો પાડો',
    retakeBtn: 'ફરીથી ફોટો લો',
    switchCameraBtn: 'કૅમેરો બદલો',
    cameraGuide: 'રોગગ્રસ્ત પાંદડું કૅમેરાની વચ્ચે સ્પષ્ટ રાખો',
    orUploadFile: 'અથવા ગૅલેરીમાંથી પાંદડાનો ફોટો પસંદ કરો',
    dropImageHere: 'અહીં ફોટો ખેંચી લાવો અથવા',
    browseFiles: 'ફાઇલ પસંદ કરો',
    analyzingImage: 'AI દ્વારા પાંદડાનું નિદાન થઈ રહ્યું છે...',
    analyzeDiseaseBtn: 'રોગ તપાસો',
    diagnosisResult: 'રોગ નિદાન રિપોર્ટ',
    cropLabel: 'પાક',
    severityLabel: 'ગંભીરતા',
    statusHealthy: 'તંદુરસ્ત પાક',
    statusDiseased: 'રોગની અસર જણાયેલ છે',
    precautionsTitle: 'પગલાંવાર સાવચેતી',
    recommendationsTitle: 'જરૂરી દવા અને ઉપચાર',
    askAssistantAboutDisease: 'આ રોગ વિશે કિસાન સહાયકને પૂછો',
    cameraPermissionDenied: 'કૅમેરાની મંજૂરી નકારી કાઢવામાં આવી છે. બ્રાઉઝર સેટિંગ્સમાં મંજૂરી આપો.',
    noCameraFound: 'આ ઉપકરણ પર કોઈ કૅમેરો મળ્યો નથી.',

    advisoryTitle: 'સ્માર્ટ પિયત અને ખેતી સલાહ',
    advisorySubtitle: 'સેન્સર આધારિત માહિતી સાથે પાણીની બચત અને ખેતરની ફળદ્રુપતા વધારો',
    cropNameLabel: 'પાકનું નામ',
    growthStageLabel: 'વિકાસનો તબક્કો',
    soilTypeLabel: 'જમીનનો પ્રકાર',
    phLabel: 'જમીનનો pH',
    moistureLabel: 'જમીનમાં ભેજ (%)',
    tempLabel: 'ખેતરનું તાપમાન (°C)',
    rainProbLabel: '24 કલાકમાં વરસાદની શક્યતા (%)',
    currentMethodLabel: 'હાલની પિયત પદ્ધતિ',
    getAdvisoryBtn: 'પિયત આયોજન મેળવો',
    calculatingAdvisory: 'જમીનના ભેજનું મૂલ્યાંકન થઈ રહ્યું છે...',
    shouldIrrigateToday: 'શું આજે પિયત આપવાની જરૂર છે?',
    irrigateYes: 'હા — આજે પિયત આપવાની ભલામણ છે',
    irrigateNo: 'ના — જમીનમાં પૂરતો ભેજ ઉપલબ્ધ છે',
    sustainabilityScore: 'જળ સંરક્ષણ સ્કોર',
    recommendedMethod: 'શ્રેષ્ઠ પિયત પદ્ધતિ',
    timetableTitle: '3-દિવસનું પિયત સમયપત્રક',
    dayLabel: 'દિવસ',
    durationLabel: 'સમય (મિનિટ)',
    waterVolumeLabel: 'પાણીનો જથ્થો',
    notesLabel: 'માર્ગદર્શન',
    soilHealthNotes: 'જમીન આરોગ્ય સંબંધિત નોંધ',
    riskFlagsTitle: 'કૃષિ જોખમ ચેતવણી',
    actionableTipsTitle: 'ખેડૂત માટે જરૂરી પગલાં',

    weatherTitle: 'હવામાન જોખમ આગાહી',
    weatherSubtitle: 'બહુ-દિવસીય કૃષિ હવામાન જોખમ વિશ્લેષણ અને અગમચેતી સલાહ',
    locationLabel: 'ખેતરનું સ્થળ / ગામ-શહેર',
    locationPlaceholder: 'શહેર કે વિસ્તારનું નામ દાખલ કરો (દા.ત. અમદાવાદ, રાજકોટ, સુરત)',
    daysAheadLabel: 'આગાહીના દિવસો',
    getForecastBtn: 'હવામાન જોખમ તપાસો',
    fetchingWeather: 'હવામાન માહિતી લાવી રહ્યું છે...',
    overallRiskTitle: 'કુલ હવામાન જોખમ સ્તર',
    riskLow: 'ઓછું જોખમ',
    riskModerate: 'મધ્યમ જોખમ',
    riskHigh: 'વધુ જોખમ',
    riskSevere: 'ગંભીર જોખમ',
    dailyForecastTitle: 'દૈનિક હવામાન અને જોખમ સ્કોર',
    rainfallLabel: 'વરસાદ',
    humidityLabel: 'ભેજ',
    windLabel: 'પવન',
    weatherRecommendations: 'હવામાન આધારિત પાક સલાહ',
    quickLocations: ['અમદાવાદ', 'રાજકોટ', 'સુરત', 'વડોદરા', 'જૂનાગઢ', 'ભાવનગર'],

    loading: 'લોડ થઈ રહ્યું છે...',
    error: 'ભૂલ આવી છે',
    dismiss: 'બંધ કરો',
    retry: 'ફરી પ્રયાસ કરો',
    success: 'સફળ',
  },
};
