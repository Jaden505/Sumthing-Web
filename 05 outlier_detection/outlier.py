from pyod.models.hbos import HBOS


def identify_outliers(features, filenames, contamination=0.1):
    # Create HBOS Weather_model
    hbos = HBOS(contamination=contamination)

    # Fit the Weather_model
    hbos.fit(features)

    # Identify outliers
    is_outlier = hbos.predict(features) == 1
    outliers = [(filenames[i], hbos.decision_scores_[i]) for i in range(len(features)) if is_outlier[i]]

    return outliers
